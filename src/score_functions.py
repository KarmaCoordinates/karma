import math

def calculate_karma_coordinates(prediction_label):
    # 5 billion years, prediction_lables are from 5-13 (in billion years)
    current_distance = 5 
    # total number of default human life existences
    possible_human_existences = 13000000000 / 100 
    dominant_satva_efficiency = 1000000
    high_satva_efficiency = 100000
    moderate_satva_efficiency = 10000
    low_satva_efficiency = 1000
    default_satva_efficiency = 100
    # Dominant satva means 1 year of life = 1000000, High satva means 1 year of life = 100000, Moderage satva means 1 year of life = 10000 years, Low satva means 1 year of life = 10 years of progress
    if prediction_label > 11:
        satva_multiplier = dominant_satva_efficiency
    elif prediction_label > 9:
        satva_multiplier = high_satva_efficiency
    elif prediction_label > 7:
        satva_multiplier = moderate_satva_efficiency
    elif prediction_label > 5:
        satva_multiplier = low_satva_efficiency
    else:
        satva_multiplier = default_satva_efficiency

    slope = (prediction_label / current_distance) * (satva_multiplier * prediction_label)
    remaining_lives = (possible_human_existences / slope)
    return f'{math.trunc(remaining_lives):,}'
    #return remaining_lives