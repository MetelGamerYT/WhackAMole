class config:
    game_name = "Jörgis Maulwurf Problem"

    default_difficulty = "Einfach"
    start_countdown_seconds = 3

    difficulties = {
        "Weichei": {
            "Time": 120,
            "MPT": 3,
            "MST": 2,
            "MissPenalty": -2.5,
        },
        "Einfach": {
            "Time": 75,
            "MPT": 3,  # Moles per Time
            "MST": 1.5,  # Sekunden Anzahl, die ein Maulwurf bleibt
            "MissPenalty": -5,  # Punkte die abgezogen werden bei einem falschen Hit
        },
        "Mittel": {
            "Time": 60,
            "MPT": 2,
            "MST": 1,
            "MissPenalty": -10,
        },
        "Schwer": {
            "Time": 30,
            "MPT": 1,
            "MST": 0.8,
            "MissPenalty": -15,
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
