test_questions = [
    {
        "q": "What is the article with the DOI 10.3233/JAD-161250?",
        "a": "MATCH (a:Article) WHERE a.doi = '10.3233/JAD-161250' RETURN a.title, a.authors, a.pubdate"
    },
    {
        "q": "List all journals with the ISO abbreviation 'J Clin Invest'.",
        "a": "MATCH (j:Journal) WHERE j.iso_abbrevation = 'J Clin Invest' RETURN j.title, j.issn_print, j.issn_online"
    },
    {
        "q": "How many times has the gene 'BRCA1' been cited in articles?",
        "a": "CALL db.index.fulltext.queryNodes(\"vocabulary_Names\", \"'BRCA1'\") YIELD node WITH node LIMIT 20 as v MATCH (a:Article)-[:ContainTerm]->(v) RETURN COUNT(DISTINCT a)"
    },
    {
        "q": "What are the diseases associated with the vocabulary term identified by 'hp:0001250'?",
        "a": "MATCH (v:Vocabulary {id: 'hp:0001250'})-[:DiseaseToPhenotypicFeatureAssociation]->(d:Vocabulary) RETURN d.name, d.id, d.n_citation LIMIT 100"
    },
    {
        "q": "Which chemical is related to the vocabulary term with ID 'chebi:17474'?",
        "a": "MATCH (c:Vocabulary {id: 'chebi:17474'})-[:ChemicalToChemicalAssociation]->(related:Vocabulary) RETURN related.name, related.id LIMIT 100"
    },
    {
        "q": "How many articles were published between 2018 and 2021?",
        "a": "MATCH (a:Article) WHERE a.pubdate >= 2018 AND a.pubdate <= 2021 RETURN COUNT(DISTINCT a)"
    },
    {
        "q": "Find the gene associated with the disease DOID:0080636.",
        "a": "MATCH (d:Vocabulary {id: 'doid:0080636'})<-[:GeneToDiseaseAssociation]-(g:Vocabulary) RETURN g.name, g.id LIMIT 100"
    },
    {
        "q": "Which articles mention the gene with HGNC ID 3432?",
        "a": "MATCH (g:Vocabulary {id: 'hgnc:3432'})<-[:ContainTerm]-(a:Article) RETURN a.title, a.pubdate LIMIT 100"
    },
    {
        "q": "What are the journals where articles about cardiovascular disease were published?",
        "a": "CALL db.index.fulltext.queryNodes(\"vocabulary_Names\", \"'cardiovascular disease'\") YIELD node AS v WITH v LIMIT 20 MATCH (a:Article)-[:ContainTerm]->(v) MATCH (a)-[:PublishedIn]->(j:Journal) RETURN DISTINCT j.title LIMIT 100"
    },
    {
        "q": "What vocabulary terms are considered synonyms of 'cholesterol'?",
        "a": "CALL db.index.fulltext.queryNodes(\"vocabulary_Names\", \"'cholesterol'\") YIELD node AS v WITH v LIMIT 20 RETURN v.synonyms LIMIT 100"
    },
    {
        "q": "What phenotypic features are linked to the genetic variant rs123698?",
        "a": "MATCH (v:Vocabulary {id: 'rs123698'})-[:VariantToDiseaseAssociation]->(d:Vocabulary)-[:DiseaseToPhenotypicFeatureAssociation]->(p:Vocabulary) RETURN p.name, p.id LIMIT 100"
    },
    {
        "q": "List articles in the database that are published in print ISSN 0028-0836.",
        "a": "MATCH (j:Journal {issn_print: '0028-0836'})<-[:PublishedIn]-(a:Article) RETURN a.title, a.pubdate LIMIT 100"
    },
    {
        "q": "Identify the diseases linked to the chemical identified by ChEBI:16015.",
        "a": "MATCH (c:Vocabulary {id: 'chebi:16015'})-[:ChemicalOrDrugOrTreatmentToDiseaseOrPhenotypicFeatureAssociation]->(d:Vocabulary) RETURN d.name, d.id LIMIT 100"
    },
    {
        "q": "Which articles are most frequently cited and published in journals with online ISSN '1476-4687'?",
        "a": "MATCH (j:Journal {issn_online: '1476-4687'})<-[:PublishedIn]-(a:Article) RETURN a.title ORDER BY a.n_citation DESC, a.pubdate DESC LIMIT 5"
    },
    {
        "q": "What are the hierarchical children of the vocabulary term 'GO:0008152'?",
        "a": "MATCH (child:Vocabulary)-[:HierarchicalStructure]->(parent:Vocabulary {id: 'go:0008152'}) RETURN child.name, child.id"
    },
    {
        "q": "What are the top 5 articles mentioning the gene 'BRCA1' by citation count?",
        "a": '''CALL db.index.fulltext.queryNodes("vocabulary_Names", "'BRCA1'") YIELD node AS gene WITH gene LIMIT 20 MATCH (article:Article)-[:ContainTerm]->(gene) RETURN article.title, article.n_citation ORDER BY article.n_citation DESC LIMIT 5'''
    },
    {
        "q": "Which diseases are associated with the gene 'TP53' and have more than 100 citations?",
        "a": '''CALL db.index.fulltext.queryNodes("vocabulary_Names", "'TP53'") YIELD node AS gene WITH gene LIMIT 20 MATCH (gene)-[:GeneToDiseaseAssociation]->(disease:Vocabulary) WHERE disease.n_citation > 100 RETURN disease.name, disease.id, disease.n_citation LIMIT 100'''
    },
    {
        "q": "List all genetic variants associated with 'diabetes' and include their risk alleles.",
        "a": '''CALL db.index.fulltext.queryNodes("vocabulary_Names", "'diabetes'") YIELD node AS disease WITH disease LIMIT 20 MATCH (variant:Vocabulary)-[:VariantToDiseaseAssociation]->(disease) RETURN variant.id, variant.name, variant.`risk allele` LIMIT 100'''
    },
    {
        "q": "What are the most cited diseases associated with chemical exposure to 'benzene'?",
        "a": '''CALL db.index.fulltext.queryNodes("vocabulary_Names", "'benzene'") YIELD node AS chemical WITH chemical LIMIT 20 MATCH (chemical)-[:ChemicalOrDrugOrTreatmentToDiseaseOrPhenotypicFeatureAssociation]->(disease:Vocabulary) RETURN disease.name, disease.id, disease.n_citation ORDER BY disease.n_citation DESC LIMIT 1'''
    },
    {
        "q": "List the diseases related to 'obesity' that also involve gene associations, returning each disease and gene.",
        "a": '''CALL db.index.fulltext.queryNodes("vocabulary_Names", "'obesity'") YIELD node AS obesity WITH obesity LIMIT 20 MATCH (disease:Vocabulary)-[:GeneToDiseaseAssociation]->(gene:Vocabulary) WHERE disease.id = obesity.id RETURN disease.name, gene.name LIMIT 100'''
    },
    {
        "q": "List all pathways associated with the gene 'EGFR' and include each pathway's description.",
        "a": '''CALL db.index.fulltext.queryNodes("vocabulary_Names", "'EGFR'") YIELD node AS gene WITH gene LIMIT 20 MATCH (gene)-[:GeneToPathwayAssociation]->(pathway:Vocabulary) RETURN pathway.name, pathway.description LIMIT 100'''
    },
    {
        "q": "What are the journals that published articles mentioning 'CRISPR' technology with more than 5 authors?",
        "a": '''CALL db.index.fulltext.queryNodes("article_Title", "'CRISPR'") YIELD node, score WITH node as n, score LIMIT 10 RETURN n, ID(n), n.id, n.title, n.n_citation, n.score'''
    },
    {
        "q": "Find all diseases that are connected to the gene with HGNC ID 'HGNC:1097' and return the disease name and its citation count.",
        "a": '''MATCH (gene:Vocabulary {id: 'hgnc:1097'})-[:GeneToDiseaseAssociation]->(disease:Vocabulary) RETURN disease.name, disease.n_citation LIMIT 100'''
    },
    {
        "q": "Which chemicals are associated with the disease 'asthma' through a gene link, and what are their respective source databases?",
        "a": '''CALL db.index.fulltext.queryNodes("vocabulary_Names", "'asthma'") YIELD node AS asthma WITH asthma LIMIT 20 MATCH (asthma)<-[:GeneToDiseaseAssociation]-(gene:Vocabulary)-[:ChemicalAffectsGeneAssociation]->(chemical:Vocabulary) RETURN chemical.name, chemical.source LIMIT 100'''
    },
    {
        "q": "List the top 5 most frequently cited vocabulary terms that are cross-referenced with other ontologies.",
        "a": '''MATCH (term:Vocabulary)-[:OntologyMapping]->(:Vocabulary) RETURN term.name, term.n_citation ORDER BY term.n_citation DESC LIMIT 5'''
    },
    {
        "q": "Identify the top 3 articles about 'epigenetics' published in 2019 with the highest citation counts.",
        "a": '''CALL db.index.fulltext.queryNodes("vocabulary_Names", "'epigenetics'") YIELD node AS epigenetics WITH epigenetics LIMIT 20 MATCH (article:Article {pubdate: 2019})-[:ContainTerm]->(epigenetics) RETURN article.title, article.n_citation ORDER BY article.n_citation DESC, article.pubdate DESC LIMIT 3'''
    },
    {
        "q": "what is TP53",
        "a": '''CALL db.index.fulltext.queryNodes("vocabulary_Names","'tp53'")YIELD node AS tp53 WITH tp53 LIMIT 20 RETURN tp53.name, tp53.id'''
    },
    {
        "q": "What are the most related genes of TP53",
        "a": '''CALL db.index.fulltext.queryNodes("vocabulary_Names", "\'TP53\'") YIELD node AS tp53 WITH tp53 LIMIT 20 MATCH (n:Gene)-[r:Similar]-(tp53) WITH n, r ORDER BY r.score DESC WITH n, COLLECT(r)[0] AS first_r RETURN n.name, n.id LIMIT 100'''
    },
    {
        "q": "What are sentence that mention association between hgnc:8515 and doid:0110535",
        "a": '''MATCH (n:Vocabulary {id: 'hgnc:8515'})-[r:Cooccur]-(n2:Vocabulary {id: 'doid:0110535'}) WHERE r.evidence IS NOT NULL WITH n, n2, r MATCH (s:Sentence) WHERE s.id IN r.evidence RETURN s.text LIMIT 200'''
    },
    {
        "q": "How are hgnc:8515 and doid:0110535 related",
        "a": '''MATCH (n:Vocabulary {id: 'hgnc:8515'})-[r:Cooccur|Similar|GeneToDiseaseAssociation]-(n2:Vocabulary {id: 'doid:0110535'}) WHERE r.evidence IS NOT NULL WITH n, n2, r MATCH (s:Sentence) WHERE s.id IN r.evidence RETURN s.text LIMIT 200'''
    },
    {
        "q": "How are hgnc:8515 and doid:0110535 related",
        "a": '''MATCH p=(v:Vocabulary {id: 'hgnc:8515'})<--(s:Article)-->(v2:Vocabulary {id: 'doid:0110535'}) RETURN DISTINCT s.pubmedid, s.title, s.abstract LIMIT 15'''
    },
]