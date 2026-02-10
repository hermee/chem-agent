"""Tests for RDKit molecular analysis (no mocking needed — pure computation)."""
from rdkit import Chem
from rdkit.Chem import QED, Descriptors, Crippen


def test_valid_smiles_ethanol():
    mol = Chem.MolFromSmiles("CCO")
    assert mol is not None
    assert Descriptors.MolWt(mol) > 40
    assert QED.qed(mol) > 0


def test_invalid_smiles():
    mol = Chem.MolFromSmiles("INVALID")
    assert mol is None


def test_lipid_like_molecule():
    """Test a simplified ionizable lipid-like structure."""
    smiles = "CCCCCCCCCCOC(=O)CC(CC(=O)OCCCCCCCCCC)N(C)C"
    mol = Chem.MolFromSmiles(smiles)
    assert mol is not None
    logp = Crippen.MolLogP(mol)
    assert logp > 3  # lipids are hydrophobic
    mw = Descriptors.MolWt(mol)
    assert 300 < mw < 1500


def test_smarts_reaction_template():
    """Test that amide formation SMARTS parses correctly."""
    smarts = "[*:1][#7:2]([H])[H,*:3].[OH,O-][C:4]([*:5])=[O:6]>>[*:5][C:4](=[O:6])[#7:2]([*:1])[H,*:3]"
    from rdkit.Chem import rdChemReactions
    rxn = rdChemReactions.ReactionFromSmarts(smarts)
    assert rxn is not None
    assert rxn.GetNumReactantTemplates() == 2
    assert rxn.GetNumProductTemplates() == 1
