import math

def calculate_karma_coordinates(category_scores, score_range):
    
    old_score = sum(category_scores.values())

    old_min = score_range['minimum_score'] 
    old_max = score_range['maximum_score']

    new_min = 1 # you have 11-1 years to go
    new_max = 10 # you have only 11-10 years to go

    old_range = old_max - old_min
    new_range = new_max - new_min

    new_score = ((old_score - old_min) / (old_max - old_min)) * (new_max - new_min) + new_min

    # 5 billion years, prediction_lables are from 5-13 (in billion years)
    current_distance = 5 
    # total number of default human life existences
    possible_human_existences = 13000000000 / 100 
    dominant_satva_efficiency = 10000000000
    high_satva_efficiency = 1000000000
    moderate_satva_efficiency = 100000000
    low_satva_efficiency = 10000000
    default_satva_efficiency = 1000000
    # Dominant satva means 1 year of life = 1000000, High satva means 1 year of life = 100000, Moderage satva means 1 year of life = 10000 years, Low satva means 1 year of life = 10 years of progress
    if new_score > 30:
        satva_multiplier = dominant_satva_efficiency
    elif new_score > 24:
        satva_multiplier = high_satva_efficiency
    elif new_score > 18:
        satva_multiplier = moderate_satva_efficiency
    elif new_score > 12:
        satva_multiplier = low_satva_efficiency
    else:
        satva_multiplier = default_satva_efficiency

    slope = (new_score / current_distance) * (satva_multiplier * new_score)
    remaining_lives = (possible_human_existences / slope)
    return f'{math.trunc(remaining_lives):,}'

def main():
    pass

if __name__ == '__main__': main()
