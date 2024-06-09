import random
import os

activities_dict = {
    1: "walking, walking on an incline, walking on a decline",
    2: "sit-to-stand from chairs with/out handles",
    3: "walking while carrying one/two shopping bags (2 to 5kg/bag)",
    4: "mopping floor",
    5: "lying on an exercise mattress",
    6: "sitting on sofa",
    7: "lying on sofa",
    8: "greeting (waving hands)",
    9: "opening a bottle of water, pouring water to a glass and drinkging from the glass",
    10: "climbing up/down stairs",
    11: "push ups",
    12: "sit up",
    13: "squat",
}


def shuffle(list_len: int = 13) -> list:
    """
    Shuffle the activities in the activities_dict
    """
    activities = list(activities_dict.keys())
    random.shuffle(activities)
    return activities[:list_len]


def list_to_file(activities: list, file_name: str = None) -> None:
    
    if file_name is None:
        file_name = input(f"please input the name of shuffled activities file (default: 'subject.txt') -> ") or "subject.txt"
    filename, extension = os.path.splitext(file_name)
    counter = 1
    while os.path.exists("multi-model-data-collector/shuffle/records/" + file_name):
        file_name = f"{filename}_{counter}{extension}"
        counter += 1
    with open("multi-model-data-collector/shuffle/records/" + file_name, "w") as f:
        for activity in activities:
            f.write(f"{activity}, {activities_dict[activity]}\n")



def main()-> None:
    shuffled_activities = shuffle()
    print(shuffled_activities)
    list_to_file(shuffled_activities)
    

if __name__ == "__main__":
    main()
    