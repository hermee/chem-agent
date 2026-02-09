"""SMARTS representations custom reactions."""
from synthemol.reactions.query_mol import QueryMol
from synthemol.reactions.reaction import Reaction

# To use custom chemical reactions instead of Enamine REAL reactions, replace None with a list of Reaction objects.
# If CUSTOM_REACTIONS is None, synthemol will default to the reactions in real.py.
#CUSTOM_REACTIONS: tuple[Reaction, ...] | None = None

CUSTOM_REACTIONS = (
    # 기존 반응: 아민 + 카르복실산 -> 아미드
    Reaction(
        reactants=[
            QueryMol("[*:1][#7:2]([H])[H,*:3]"),
            QueryMol("[OH,O-][C:4]([*:5])=[O:6]"),
        ],
        product=QueryMol("[*:5][C:4](=[O:6])[#7:2]([*:1])[H,*:3]"),
        chemical_space="custom",
        reaction_id=10001,
    ),

    # 카르복실산 + 하이드록실기 반응 (에스터 형성)
     Reaction(
        reactants=[
            QueryMol("[OH,O-][C:1]([*:2])=[O:3]"),
            QueryMol("[*:4][OH:5]"),
        ],
        product=QueryMol("[*:2][C:1](=[O:3])[O:5][*:4]"),
        chemical_space="custom",
        reaction_id=10003,
    ),


    # 아민기 + 하이드록실기(-OH) 반응 (아민 알킬화)
    Reaction(
        reactants=[
            QueryMol("[*:1][#7:2]([H])[H,*:3]"),
            QueryMol("[*:4][CH2:5][OH:6]"),
        ],
        product=QueryMol("[*:1][#7:2]([*:3])[C:5][*:4]"),
        chemical_space="custom",
        reaction_id=10005,
    ),
    
    # 아민기 + -SH 반응 (티오에테르 형성)
    Reaction(
        reactants=[
            QueryMol("[*:1][#7:2]([H])[H,*:3]"),
            QueryMol("[*:4][CH2:5][SH:6]"),
        ],
        product=QueryMol("[*:1][#7:2]([*:3])[C:5][*:4]"),
         chemical_space="custom",
        reaction_id=10007,
    ),

     # 아민기 + epoxide 반응 (에폭사이드 개환)
    Reaction(
        reactants=[
            QueryMol("[*:1][#7:2]([H])[H,*:3]"),
            QueryMol("[*:4][CH:5]1[O:6][CH2:7]1"),
        ],
        product=QueryMol("[*:1][#7:2]([*:3])[C:7][C:5]([OH])[*:4]"),
        chemical_space="custom",
        reaction_id=10009,
    ),
    # 아민기 + alkyl-acrylate 반응 (Michael 부가)
    Reaction(
        reactants=[
            QueryMol("[*:1][#7:2]([H])[H,*:3]"),
            QueryMol("[*:4][O:5][C:6](=[O:7])[CH:8]=[CH2:9]"),
        ],
        product=QueryMol("[*:1][#7:2]([*:3])[C:9][C:8][C:6](=[O:7])[O:5][*:4]"),
        chemical_space="custom",
        reaction_id=10010,
    ),

    # 아민기 + alkyl-acrylamide 반응 (Michael 부가)
    Reaction(
        reactants=[
            QueryMol("[*:1][#7:2]([H])[H,*:3]"),
            QueryMol("[*:4][#7:5]([H])[C:6](=[O:7])[CH:8]=[CH2:9]"),
        ],
        product=QueryMol("[*:1][#7:2]([*:3])[C:9][C:8][C:6](=[O:7])[#7:5]([H])[*:4]"),
        chemical_space="custom",
        reaction_id=10011,
    ),

     # 아민기 + -CH3 반응 (N-메틸화, 촉매 존재)
    Reaction(
        reactants=[
            QueryMol("[*:1][#7:2]([H])[H,*:3]"),
            QueryMol("[*:4][CH3:5]"),
        ],
        product=QueryMol("[*:1][#7:2]([*:3])[C:5]"),
        chemical_space="custom",
        reaction_id=10012,
    ),
    
    # tertiary amine + alkylated dioxaphospholane oxide 반응 (암모늄-인산염 형성)
    Reaction(
        reactants=[
            QueryMol("[*:1][N:2]([*:3])[*:4]"),
            QueryMol("[*:5][O:6][P:7]1(=[O:8])[O:9][CH2:10][CH2:11][O:12]1"),
        ],
        product=QueryMol("[*:1][N+:2]([*:3])([*:4])[C:10][C:11][O:12][P:7]([O:9])([O:6][*:5])=[O:8]"),
        chemical_space="custom",
        reaction_id=10013,
    ),

    Reaction(
        reactants=[
            QueryMol("[*:1][#7:2]([*:3])[*:4]"),
            QueryMol("[*:5][O:6][P:7](=[O:8])[O:9][CH2:10][CH2:11][O:12]"),
        ],
        product=QueryMol("[*:1][#7+:2]([*:3])([*:4])[C:10][C:11][O:12][P:7]([O-:9])([O:6][*:5])=[O:8]"),
        chemical_space="custom",
        reaction_id=10014,
    ),

    Reaction(
        reactants=[
            QueryMol("[*:1][#7:2]([H])[H]"),  # 1차 아민
            QueryMol("[*:4][CH:5]=[O:6]"),        # 알데히드
        ],
        product=QueryMol("[*:1][#7:2]=[C:5][*:4]"),  # 이민
        chemical_space="custom",
        reaction_id=10015,
    ),

    Reaction(
        reactants=[
            QueryMol("[*:1][#7:2]([H])[*:3]"),    # 2차 아민
            QueryMol("[*:4][CH:5]=[O:6]"),        # 알데히드
        ],
        product=QueryMol("[*:1][#7:2]([*:3])[C:5][*:4]"),  # 3차 아민
        chemical_space="custom",
        reaction_id=10016,
    ),

   # 아민 + 알데히드 → 아미드 (역순)
    Reaction(
        reactants=[
            QueryMol("[*:1][#7:2]([H])[H]"), # 1차 아민
            QueryMol("[*:4][CH:5]=[O:6]"),       # 알데히드
        ],
        product=QueryMol("[*:4][C:5](=[O:6])[#7:2]([*:1])[H]"),  # 아미드
        chemical_space="custom",
        reaction_id=10017,
    ),
)
