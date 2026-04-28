class config:
    game_name = "Jörgis Maulwurf Problem"

    default_difficulty = "Einfach"
    start_countdown_seconds = 3

    difficulties = {
        "Einfach": {
            "Time": 120,
            "MPT": 3,  # Moles per Time
            "MST": 1.5,  # Sekunden Anzahl, die ein Maulwurf bleibt
            "MissPenalty": -5,  # Punkte die Abgezogen werden bei einem falschen Hit
        },
        "Mittel": {
            "Time": 90,
            "MPT": 2,
            "MST": 1,
            "MissPenalty": -10,
        },
        "Schwer": {
            "Time": 60,
            "MPT": 1,
            "MST": 0.5,
            "MissPenalty": -15,
        },
        "Albtraum": {
            "Time": 60,
            "MPT": 1,
            "MST": 0.35,
            "MissPenalty": -30,
        },
    }

    @classmethod
    def difficulty_names(cls):
        return tuple(cls.difficulties.keys())

    @classmethod
    def get_difficulty(cls, difficulty_name):
        return cls.difficulties.get(
            difficulty_name,
            cls.difficulties[cls.default_difficulty],
        )
