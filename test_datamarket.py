"""
Tests de validation - DataMarket Senegal
========================================
Lancement :  pytest -v test_datamarket.py

Couvre les quatre modules : integrite du pipeline, coherence arithmetique
des calculs TAM/SAM/SOM, robustesse de l'extraction d'intention, generation
du rapport PDF.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

import config
import market
import nlp_agent
import territory
from pipeline import (
    JeuDeDonnees, charger_donnees, nettoyer_nombre, normaliser_region, preparer,
)


# ==========================================================================
# Fixtures
# ==========================================================================

@pytest.fixture(scope="module")
def jeu() -> JeuDeDonnees:
    return charger_donnees()


# ==========================================================================
# MODULE 1 - Pipeline
# ==========================================================================

class TestNormalisationRegions:

    def test_les_14_regions_sont_reconnues(self):
        for region in config.REGIONS:
            assert normaliser_region(region) == region

    @pytest.mark.parametrize("saisie,attendu", [
        ("THIÈS", "Thies"),
        ("thies", "Thies"),
        ("Région de Thiès", "Thies"),
        ("SAINT LOUIS", "Saint-Louis"),
        ("St Louis", "Saint-Louis"),
        ("Sédhiou", "Sedhiou"),
        ("KÉDOUGOU", "Kedougou"),
        ("  Dakar  ", "Dakar"),
        ("Ziguinchor (ZG)", "Ziguinchor"),
    ])
    def test_variantes_orthographiques(self, saisie, attendu):
        assert normaliser_region(saisie) == attendu

    @pytest.mark.parametrize("saisie", [
        "Sénégal", "Total", "Ensemble", "National", "", None, "Urbain",
    ])
    def test_lignes_agregat_rejetees(self, saisie):
        assert normaliser_region(saisie) is None

    def test_ville_mappee_vers_sa_region(self):
        assert normaliser_region("Mbour") == "Thies"
        assert normaliser_region("Touba") == "Diourbel"
        assert normaliser_region("Pikine") == "Dakar"


class TestNettoyageNombres:

    @pytest.mark.parametrize("saisie,attendu", [
        ("1 234 567", 1234567.0),
        ("1 234 567", 1234567.0),       # espace insecable
        ("542 706 FCFA", 542706.0),
        ("12,5", 12.5),
        ("1.234.567,89", 1234567.89),
        ("1,234,567.89", 1234567.89),
        ("45%", 45.0),
        ("(1000)", -1000.0),
        (15000, 15000.0),
        (3.5, 3.5),
    ])
    def test_conversions(self, saisie, attendu):
        assert nettoyer_nombre(saisie) == pytest.approx(attendu)

    @pytest.mark.parametrize("saisie", ["", "n/d", "-", "..", None, "abc"])
    def test_valeurs_manquantes(self, saisie):
        assert np.isnan(nettoyer_nombre(saisie))


class TestChargement:

    def test_exactement_14_regions_par_bloc(self, jeu):
        for bloc in (jeu.population, jeu.depenses, jeu.production):
            assert len(bloc) == 14
            assert set(bloc["region"]) == set(config.REGIONS)

    def test_aucune_population_manquante(self, jeu):
        assert jeu.population["population"].notna().all()
        assert (jeu.population["population"] > 0).all()

    def test_total_conforme_au_rgph5(self, jeu):
        total = jeu.population["population"].sum()
        ecart = abs(total - config.POPULATION_NATIONALE) / config.POPULATION_NATIONALE
        assert ecart < 0.01, (
            f"Total {total:,.0f} contre {config.POPULATION_NATIONALE:,.0f} "
            f"attendu (écart {ecart:.2%})")

    def test_parts_nationales_somment_a_100(self, jeu):
        assert jeu.population["part_nationale_pct"].sum() == pytest.approx(100, abs=0.01)

    def test_dakar_est_la_region_la_plus_peuplee(self, jeu):
        tete = jeu.population.nlargest(1, "population").iloc[0]
        assert tete["region"] == "Dakar"

    def test_hierarchie_des_trois_premieres_regions(self, jeu):
        ordre = jeu.population.nlargest(3, "population")["region"].tolist()
        assert ordre == ["Dakar", "Thies", "Diourbel"]

    def test_densite_de_dakar_conforme(self, jeu):
        """RGPH-5 publie 7 277 hab/km2 pour Dakar."""
        dakar = jeu.population.set_index("region").loc["Dakar"]
        assert dakar["densite"] == pytest.approx(7277, rel=0.05)

    def test_depense_moyenne_ponderee_recalee_sur_ehcvm(self, jeu):
        fusion = jeu.population[["region", "population"]].merge(
            jeu.depenses[["region", "depense_tete"]], on="region")
        moyenne = np.average(fusion["depense_tete"],
                             weights=fusion["population"])
        assert moyenne == pytest.approx(config.DEPENSE_ANNUELLE_TETE, rel=0.001)

    def test_dakar_a_la_depense_par_tete_la_plus_elevee(self, jeu):
        tete = jeu.depenses.nlargest(1, "depense_tete").iloc[0]
        assert tete["region"] == "Dakar"

    def test_urbain_plus_rural_egale_population(self, jeu):
        pop = jeu.population
        somme = pop["population_urbaine"] + pop["population_rurale"]
        assert np.allclose(somme, pop["population"])

    def test_taux_urbanisation_national_coherent(self, jeu):
        pop = jeu.population
        taux = 100 * pop["population_urbaine"].sum() / pop["population"].sum()
        assert taux == pytest.approx(config.TAUX_URBANISATION_NATIONAL, abs=1.5)

    def test_coefficients_budgetaires_somment_a_100(self, jeu):
        colonnes = [c for c in jeu.depenses.columns
                    if c.startswith("part_") and c.endswith("_pct")]
        sommes = jeu.depenses[colonnes].sum(axis=1)
        assert np.allclose(sommes, 100, atol=0.5)

    def test_production_totale_egale_somme_des_cultures(self, jeu):
        prod = jeu.production
        cultures = [c for c in prod.columns
                    if c.endswith("_t") and c != "production_totale_t"]
        assert np.allclose(prod[cultures].sum(axis=1), prod["production_totale_t"])

    def test_vue_consolidee(self, jeu):
        consolide = jeu.consolide
        assert len(consolide) == 14
        for colonne in ("population", "depense_tete", "part_alimentation_pct",
                        "production_totale_t", "population_urbaine"):
            assert colonne in consolide.columns


class TestIngestionUtilisateur:

    def test_csv_utilisateur_ecrase_la_reference(self, tmp_path):
        """Un CSV depose par l'utilisateur doit primer sur la valeur livree."""
        dossier = tmp_path / "raw"
        dossier.mkdir()
        (dossier / "pop.csv").write_text(
            "Région;Population totale\n"
            "Dakar;5 000 000\n"
            "Thiès;2 500 000\n"
            "Diourbel;2 100 000\n"
            "Kaolack;1 300 000\n"
            "Saint-Louis;1 200 000\n"
            "Louga;1 100 000\n"
            "Fatick;1 000 000\n"
            "Tambacounda;950 000\n"
            "Kolda;900 000\n"
            "Matam;760 000\n"
            "Kaffrine;760 000\n"
            "Ziguinchor;600 000\n"
            "Sédhiou;600 000\n"
            "Kédougou;250 000\n"
            "Sénégal;19 020 000\n",
            encoding="utf-8",
        )
        jeu = charger_donnees(dossier_brut=dossier)
        dakar = jeu.population.set_index("region").loc["Dakar", "population"]
        assert dakar == 5_000_000
        assert len(jeu.population) == 14   # la ligne "Sénégal" est ecartee

    def test_fichier_illisible_ignore_sans_erreur(self, tmp_path):
        dossier = tmp_path / "raw"
        dossier.mkdir()
        (dossier / "bruit.csv").write_text("bla bla bla\n", encoding="utf-8")
        jeu = charger_donnees(dossier_brut=dossier)
        assert len(jeu.population) == 14

    def test_donnees_departementales_agregees_par_region(self):
        """Plusieurs lignes d'une meme region doivent etre sommees."""
        brut = pd.DataFrame({
            "region": ["Dakar", "Dakar", "Thiès", "Thiès"],
            "population": [1_182_416, 2_823_516, 937_189, 1_528_000],
        })
        propre = preparer(brut)
        assert len(propre) == 2
        dakar = propre.set_index("region").loc["Dakar", "population"]
        assert dakar == pytest.approx(4_005_932)


# ==========================================================================
# MODULE 2 - TAM / SAM / SOM
# ==========================================================================

class TestCalculsMarche:

    @pytest.mark.parametrize("secteur", list(config.SECTEURS))
    def test_hierarchie_tam_sam_som(self, jeu, secteur):
        r = market.calculer(jeu, secteur)
        assert r.tam > 0
        assert r.tam >= r.sam >= r.som > 0

    @pytest.mark.parametrize("secteur", list(config.SECTEURS))
    def test_sam_est_bien_le_produit_attendu(self, jeu, secteur):
        r = market.calculer(jeu, secteur, part_geographique=0.25)
        assert r.sam == pytest.approx(r.tam * 0.25)

    @pytest.mark.parametrize("secteur", list(config.SECTEURS))
    def test_som_est_bien_le_produit_attendu(self, jeu, secteur):
        r = market.calculer(jeu, secteur, part_geographique=0.5,
                            part_marche_visee=0.04)
        assert r.som == pytest.approx(r.sam * 0.04)

    @pytest.mark.parametrize("secteur", list(config.SECTEURS))
    def test_somme_des_regions_egale_le_total(self, jeu, secteur):
        r = market.calculer(jeu, secteur)
        assert r.detail_regional["tam_region"].sum() == pytest.approx(r.tam)
        assert r.detail_regional["sam_region"].sum() == pytest.approx(r.sam)
        assert r.detail_regional["som_region"].sum() == pytest.approx(r.som)

    @pytest.mark.parametrize("secteur", list(config.SECTEURS))
    def test_parts_regionales_somment_a_100(self, jeu, secteur):
        r = market.calculer(jeu, secteur)
        assert r.detail_regional["part_tam_pct"].sum() == pytest.approx(100, abs=0.01)

    def test_additivite_geographique(self, jeu):
        """TAM(A) + TAM(B) doit egaler TAM(A et B)."""
        a = market.calculer(jeu, "commerce_proximite", regions=["Dakar"])
        b = market.calculer(jeu, "commerce_proximite", regions=["Thies"])
        ensemble = market.calculer(jeu, "commerce_proximite",
                                   regions=["Dakar", "Thies"])
        assert ensemble.tam == pytest.approx(a.tam + b.tam)

    def test_tam_national_borne_par_la_depense_totale(self, jeu):
        """Le TAM ne peut jamais depasser la depense totale des menages."""
        depense_totale = config.POPULATION_NATIONALE * config.DEPENSE_ANNUELLE_TETE
        for secteur in config.SECTEURS:
            r = market.calculer(jeu, secteur)
            assert r.tam < depense_totale, (
                f"{secteur} : TAM de {r.tam:,.0f} supérieur à la dépense "
                f"nationale totale de {depense_totale:,.0f}")

    def test_commerce_proximite_reste_sous_le_budget_alimentaire(self, jeu):
        """Le TAM du commerce ne peut exceder le budget alimentaire national."""
        r = market.calculer(jeu, "commerce_proximite")
        consolide = jeu.consolide
        budget_alimentaire = (
            consolide["population"] * consolide["depense_tete"]
            * consolide["part_alimentation_pct"] / 100
        ).sum()
        # Le panier inclut l'hygiene : on tolere la majoration correspondante
        plafond = budget_alimentaire * 1.15
        assert r.tam <= plafond

    def test_restauration_sante_est_une_niche(self, jeu):
        """La cible doit rester une petite fraction de la population."""
        r = market.calculer(jeu, "restauration_sante")
        part = r.population_cible / config.POPULATION_NATIONALE
        assert 0.0005 < part < 0.05, f"Part de la population ciblée : {part:.2%}"

    def test_commerce_cible_toute_la_population(self, jeu):
        r = market.calculer(jeu, "commerce_proximite")
        assert r.population_cible == pytest.approx(
            config.POPULATION_NATIONALE, rel=0.01)

    def test_agrobusiness_nul_sans_production(self, jeu):
        """Une region sans production agricole a un potentiel de transformation nul."""
        r = market.calculer(jeu, "agrobusiness")
        detail = r.detail_regional
        sans_prod = detail[detail["production_totale_t"] <= 0]
        assert (sans_prod["tam_region"] == 0).all()

    def test_budget_insuffisant_reduit_le_som(self, jeu):
        capex = config.SECTEURS["commerce_proximite"]["capex_min_fcfa"]
        riche = market.calculer(jeu, "commerce_proximite", budget=capex)
        pauvre = market.calculer(jeu, "commerce_proximite", budget=capex // 10)
        assert pauvre.som < riche.som
        assert pauvre.avertissements

    def test_budget_confortable_ne_reduit_pas_le_som(self, jeu):
        capex = config.SECTEURS["commerce_proximite"]["capex_min_fcfa"]
        reference = market.calculer(jeu, "commerce_proximite")
        finance = market.calculer(jeu, "commerce_proximite", budget=capex * 2)
        assert finance.som >= reference.som

    def test_parts_bornees_entre_0_et_1(self, jeu):
        r = market.calculer(jeu, "commerce_proximite",
                            part_geographique=5.0, part_marche_visee=-2.0)
        assert r.sam == pytest.approx(r.tam)   # borne a 1.0
        assert r.som == pytest.approx(0.0)     # borne a 0.0

    def test_secteur_inconnu_leve_une_erreur(self, jeu):
        with pytest.raises(KeyError):
            market.calculer(jeu, "cryptomonnaie")

    def test_region_invalide_bascule_en_national(self, jeu):
        r = market.calculer(jeu, "commerce_proximite", regions=["Atlantide"])
        assert len(r.regions) == 14

    def test_ca_mensuel_coherent(self, jeu):
        r = market.calculer(jeu, "commerce_proximite")
        assert r.ca_mensuel_som == pytest.approx(r.som / 12)


class TestClassementRegional:

    @pytest.mark.parametrize("secteur", list(config.SECTEURS))
    def test_14_regions_classees(self, jeu, secteur):
        p = market.potentiel_par_region(jeu, secteur)
        assert len(p) == 14
        assert p["score_potentiel"].between(0, 100).all()

    def test_dakar_domine_le_commerce_de_proximite(self, jeu):
        p = market.potentiel_par_region(jeu, "commerce_proximite")
        assert p.iloc[0]["region"] == "Dakar"

    def test_classement_decroissant(self, jeu):
        p = market.potentiel_par_region(jeu, "commerce_proximite")
        scores = p["score_potentiel"].tolist()
        assert scores == sorted(scores, reverse=True)

    def test_comparaison_des_trois_secteurs(self, jeu):
        c = market.comparer_secteurs(jeu)
        assert len(c) == 3
        assert (c["TAM (FCFA)"] > 0).all()
        assert (c["TAM (FCFA)"] >= c["SAM (FCFA)"]).all()


# ==========================================================================
# MODULE 3 - Interface conversationnelle
# ==========================================================================

class TestTerritoryEngine:

    def test_46_departements_sur_14_regions(self):
        assert len(territory.DEPARTEMENTS) == 14
        assert sum(len(d) for d in territory.DEPARTEMENTS.values()) == 46

    def test_chaque_departement_rattache_a_une_region_du_referentiel(self):
        for region in territory.DEPARTEMENTS:
            assert region in config.REGIONS

    def test_mbour_est_ambigu(self):
        resolution = territory.resoudre_territoire("Mbour")
        assert resolution is not None
        assert resolution.ambigu
        assert resolution.region == "Thies"
        assert len(resolution.interpretations) == 2

    def test_region_du_departement(self):
        assert territory.region_du_departement("Mbour") == "Thies"
        assert territory.region_du_departement("Bignona") == "Ziguinchor"
        assert territory.region_du_departement("Inconnu") is None

    @pytest.mark.parametrize("saisie", ["mbour", "MBOUR", "Mbour", " mbour "])
    def test_resolution_insensible_a_la_casse_et_aux_espaces(self, saisie):
        resolution = territory.resoudre_territoire(saisie)
        assert resolution is not None and resolution.region == "Thies"

    def test_ville_simple_non_ambigue(self):
        # Touba est une ville du referentiel mais n'est pas elle-meme un nom
        # de departement (elle releve du departement de Mbacke) : pas
        # d'ambiguite commune/departement.
        resolution = territory.resoudre_territoire("Touba")
        assert resolution is not None
        assert resolution.region == "Diourbel"
        assert not resolution.ambigu

    def test_territoire_inconnu_retourne_none(self):
        assert territory.resoudre_territoire("Atlantide") is None
        assert territory.resoudre_territoire("") is None

    def test_ambiguite_remonte_dans_les_notes_de_intention(self):
        intention = nlp_agent.analyser_local("Je veux ouvrir une supérette à Mbour")
        assert any("commune" in n and "département" in n for n in intention.notes)


class TestExtractionIntention:

    @pytest.mark.parametrize("phrase,secteur", [
        ("Je veux ouvrir une supérette à Mbour", "commerce_proximite"),
        ("Ouvrir une boutique de quartier", "commerce_proximite"),
        ("Monter une épicerie à Pikine", "commerce_proximite"),
        ("Un restaurant pour diabétiques", "restauration_sante"),
        ("Traiteur santé et nutrition à Dakar", "restauration_sante"),
        ("Cantine diététique sans sucre", "restauration_sante"),
        ("Unité de transformation d'arachide", "agrobusiness"),
        ("Usine de jus de mangue", "agrobusiness"),
        ("Minoterie de mil à Kaffrine", "agrobusiness"),
    ])
    def test_secteur_detecte(self, phrase, secteur):
        assert nlp_agent.analyser_local(phrase).secteur == secteur

    @pytest.mark.parametrize("phrase,region", [
        ("supérette à Mbour", "Thies"),
        ("boutique à Touba", "Diourbel"),
        ("commerce à Pikine", "Dakar"),
        ("restaurant à Richard-Toll", "Saint-Louis"),
        ("épicerie à Ourossogui", "Matam"),
        ("magasin à Ziguinchor", "Ziguinchor"),
        ("boutique à Kédougou", "Kedougou"),
    ])
    def test_ville_mappee_vers_region(self, phrase, region):
        assert nlp_agent.analyser_local(phrase).regions == [region]

    def test_absence_de_lieu_donne_le_national(self):
        intention = nlp_agent.analyser_local("Je veux ouvrir une boutique")
        assert len(intention.regions) == 14

    @pytest.mark.parametrize("phrase,budget", [
        ("supérette avec 15 millions", 15_000_000),
        ("budget de 2,5 millions", 2_500_000),
        ("j'ai 500 mille francs", 500_000),
        ("investir 1 milliard", 1_000_000_000),
        ("avec 8 000 000 FCFA", 8_000_000),
        ("quinze millions de budget", 15_000_000),
    ])
    def test_budget_extrait(self, phrase, budget):
        assert nlp_agent.analyser_local(phrase).budget == pytest.approx(budget)

    def test_budget_absent(self):
        assert nlp_agent.analyser_local("ouvrir une boutique").budget is None

    def test_part_de_marche_explicite(self):
        intention = nlp_agent.analyser_local(
            "boutique à Dakar, je vise 5% du marché")
        assert intention.part_marche_visee == pytest.approx(0.05)

    def test_echelle_quartier_restreint_le_sam(self):
        intention = nlp_agent.analyser_local("une boutique de quartier à Touba")
        assert intention.part_geographique <= 0.03

    def test_phrase_vide_ne_plante_pas(self):
        intention = nlp_agent.analyser_local("")
        assert intention.secteur in config.SECTEURS
        assert len(intention.regions) == 14

    def test_phrase_absurde_retombe_sur_un_defaut(self):
        intention = nlp_agent.analyser_local("azerty qwerty 123")
        assert intention.secteur in config.SECTEURS
        assert intention.confiance < 0.5

    def test_confiance_bornee(self):
        for phrase in ["", "supérette à Mbour avec 15 millions", "xyz"]:
            c = nlp_agent.analyser_local(phrase).confiance
            assert 0 <= c <= 1

    def test_chaine_complete(self, jeu):
        intention, resultat = nlp_agent.interroger(
            jeu, "Je veux ouvrir une supérette à Mbour avec 15 millions",
            forcer_local=True)
        assert intention.secteur == "commerce_proximite"
        assert intention.regions == ["Thies"]
        assert intention.budget == 15_000_000
        assert resultat.tam > 0
        assert resultat.tam >= resultat.sam >= resultat.som > 0

    def test_analyser_ne_leve_jamais(self, jeu):
        for phrase in ["", "   ", "?!@#$", "a" * 500, "Мбур"]:
            intention = nlp_agent.analyser(phrase, forcer_local=True)
            assert intention.secteur in config.SECTEURS


class TestSynthese:

    def test_synthese_locale_non_vide(self, jeu):
        intention, resultat = nlp_agent.interroger(
            jeu, "supérette à Mbour", forcer_local=True)
        texte = nlp_agent.synthese_locale(intention, resultat)
        assert len(texte) > 200
        assert "FCFA" in texte


# ==========================================================================
# MODULE 4 - Export
# ==========================================================================

class TestRapport:

    def test_generation_pdf(self, jeu, tmp_path):
        from report import generer_rapport

        r = market.calculer(jeu, "commerce_proximite", regions=["Thies"],
                            part_geographique=0.38, budget=15_000_000)
        chemin = generer_rapport(
            r, chemin=tmp_path / "test.pdf",
            synthese="Synthèse de test.",
            intention_brute="supérette à Mbour")
        assert chemin.exists()
        assert chemin.stat().st_size > 5000
        assert chemin.read_bytes()[:4] == b"%PDF"

    @pytest.mark.parametrize("secteur", list(config.SECTEURS))
    def test_pdf_pour_chaque_secteur(self, jeu, tmp_path, secteur):
        from report import generer_rapport

        r = market.calculer(jeu, secteur)
        chemin = generer_rapport(r, chemin=tmp_path / f"{secteur}.pdf")
        assert chemin.exists() and chemin.stat().st_size > 5000


class TestVisualisation:

    @pytest.mark.parametrize("secteur", list(config.SECTEURS))
    def test_graphiques_se_construisent(self, jeu, secteur):
        import dashboard

        p = market.potentiel_par_region(jeu, secteur)
        r = market.calculer(jeu, secteur)
        assert dashboard.graphique_tam_regions(p) is not None
        assert dashboard.graphique_entonnoir(r) is not None
        assert dashboard.graphique_structure(p) is not None
        assert dashboard.graphique_production(jeu.production) is not None

    def test_carte_en_mode_degrade(self, jeu):
        import dashboard
        from geo import Geographie

        p = market.potentiel_par_region(jeu, "commerce_proximite")
        carte = dashboard.carte_potentiel(
            p, Geographie(None, "cercles", "test"))
        assert carte is not None


# ==========================================================================
# Coherence transversale
# ==========================================================================

class TestCoherenceGlobale:

    def test_referentiel_a_bien_14_regions(self):
        assert len(config.REGIONS) == 14
        assert len(set(config.REGIONS)) == 14

    def test_chaque_region_a_un_centroide(self):
        for region in config.REGIONS:
            assert region in config.CENTROIDES
            lat, lon = config.CENTROIDES[region]
            assert 12 <= lat <= 17, f"{region} : latitude hors du Sénégal"
            assert -18 <= lon <= -11, f"{region} : longitude hors du Sénégal"

    def test_chaque_region_a_un_libelle_affichage(self):
        for region in config.REGIONS:
            assert config.REGIONS_AFFICHAGE.get(region)

    def test_toutes_les_villes_pointent_vers_une_region_valide(self):
        for ville, region in config.VILLES_VERS_REGION.items():
            assert region in config.REGIONS, f"{ville} -> {region} invalide"

    def test_les_trois_secteurs_sont_configures(self):
        assert set(config.SECTEURS) == {
            "commerce_proximite", "restauration_sante", "agrobusiness"}
        for cle, parametres in config.SECTEURS.items():
            for champ in ("libelle", "description", "sam_defaut", "som_defaut"):
                assert champ in parametres, f"{cle} : '{champ}' manquant"
            assert 0 < parametres["sam_defaut"] <= 1
            assert 0 < parametres["som_defaut"] <= 1

    @pytest.mark.parametrize("montant,attendu", [
        (850, "850 FCFA"),
        (12_000, "12 k FCFA"),
        (2_500_000, "2.5 M FCFA"),
        (3_200_000_000, "3.2 Md FCFA"),
    ])
    def test_formatage_des_montants(self, montant, attendu):
        assert config.formater_fcfa(montant) == attendu

    def test_formatage_des_nombres(self):
        assert config.formater_nombre(1234567) == "1 234 567"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
