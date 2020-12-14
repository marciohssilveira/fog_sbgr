import math

def calculate_rh(temperature, dew):
    """
    Receives air temperature (t) and dew point (d) and returns relative humidity
    RH = 100*(EXP((17.625*TD)/(243.04+TD))/EXP((17.625*T)/(243.04+T)))
    """
    rh_list = []
    for t, d in zip(temperature, dew):
        rh = 100 * ((math.exp((17.625 * d) / (243.04 + d))) /
                    (math.exp((17.625 * t) / (243.04 + t))))
        rh_list.append(rh)
    return rh_list