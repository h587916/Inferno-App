plotting_combinations = [
    {
        'id': 1,
        'Y': pd.DataFrame({'diff.MDS.UPRS.III': list(range(-10, 11))}),  # Y range from -30 to 30
        'X': pd.DataFrame({'Sex': ['Female'], 'TreatmentGroup': ['NR']})
    },
    {
        'id': 2,
        'Y': pd.DataFrame({'diff.MDS.UPRS.III': list(range(-10, 11))}),  # Y range from -30 to 30
        'X': pd.DataFrame({'Sex': ['Male', 'Male'], 'TreatmentGroup': ['NR', 'Placebo']})  # Multiple categories
    },
    {
        'id': 3,
        'Y': pd.DataFrame({'diff.MDS.UPRS.III': list(range(-10, 11))}),  # Y range from -30 to 30
        'X': pd.DataFrame({'Sex': ['Female'] * len(list(range(25, 31))), 'Age': list(range(25, 31)), 'TreatmentGroup': ['NR'] * len(list(range(25, 31)))})  # Age range
    },
    {
        'id': 4,
        'Y': pd.DataFrame({'diff.MDS.UPRS.III': [0]}),  # Single value
        'X': pd.DataFrame({'Sex': ['Female'] * len(list(range(25, 31))), 'Age': list(range(25, 31)), 'TreatmentGroup': ['NR'] * len(list(range(25, 31)))})  # Age range
    },
]

value_combinations = [
    {
        'id': 5,
        'Y': pd.DataFrame({'diff.MDS.UPRS.III': [0]}),  # Single value
        'X': pd.DataFrame({'Sex': ['Female'], 'TreatmentGroup': ['NR']})
    },
    {
        'id': 6,
        'Y': pd.DataFrame({'diff.MDS.UPRS.III': [0]}),  # Single value
        'X': pd.DataFrame({'Sex': ['Male', 'Male'], 'TreatmentGroup': ['NR', 'Placebo']})  # Multiple categories
    }
]