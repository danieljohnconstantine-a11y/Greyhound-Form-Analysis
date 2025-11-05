# config.py
SCORING_WEIGHTS = {
    "win": 5,               # Points per career win
    "place": 2,             # Points per career place (2nd/3rd)
    "money": 0.0001,        # Points per $1 prize money (small because amounts are large)
    "dlw_penalty": 0.05,    # Small penalty per day since last win
    "rtc_boost": 0.5,       # Boost for RTC (if available)
    "speed": 0.1,           # Points per km/h speed
    "early_speed": 0.2,     # Points per early speed index
    "form": 1,              # Multiplier for form score
    "box_advantage": 2,     # Bonus for good box (1-4)
    "box_disadvantage": 1,  # Penalty for bad box (7-8)
    "trainer": 3,           # Bonus for successful trainer
    
    "win_threshold": 60,    # Minimum score for Win bet
    "place_threshold": 45,  # Minimum score for Place bet
}