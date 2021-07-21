from datetime import datetime, timezone
import getpass
import random
import json
import argparse
from faker import Faker


def percent_roll_check(threshold: int):
    """    
    Roll a d100 and see if you pass the check
    """

    if random.randint(0, 100) <= threshold:
        return False
    
    return True


def get_random_items(from_list, max_items: int, chance_is_empty: int = 0):    
    """
    From a given iterable `from_list` get up to `max_items` number of items as a set
    Additionally there is a `chance_is_empty` percent that returned set is empty
    """

    if chance_is_empty:
        if not percent_roll_check(chance_is_empty):
            return set()
    
    result = list()
    number_of_items = random.randint(1, max_items)

    for _ in range(number_of_items):
        random_index = random.randint(0, len(from_list)-1)
        result.append(from_list[random_index])
    
    # converting to a set removes duplicates as
    # we haven't sampled without replacement
    return set(result)


def generate_meta_data(fake: Faker, number_of_records: int, random_seed: int):
    meta_data = dict()

    generated_at = datetime.now()

    meta_data["generated_at"] = {
        "local": {
            "date": generated_at.date().isoformat(),
            "time": generated_at.time().isoformat(),        
        },
        "timestamp": generated_at.astimezone(timezone.utc).isoformat()

    }
    meta_data["user"] = getpass.getuser()
    meta_data["number_of_records"] = number_of_records
    meta_data["random_seed"] = random_seed

    return meta_data


def generate_people(fake: Faker, number_of_people: int):
    # list of instagram tags
    tags = [
        '#love', '#fashion', '#photooftheday', '#beautiful', '#photography',
        '#picoftheday', '#happy', '#follow', '#nature', '#tbt', '#instagram',
        '#travel', '#like4like', '#style', '#repost', '#summer', '#instadaily',
        '#selfie', '#beauty', '#girl', '#friends', '#instalike', '#me', 
        '#smile', '#family', '#photo', '#life', '#likeforlike', '#music',
        '#ootd', '#makeup', '#follow4follow', '#amazing', '#igers', '#nofilter',
        '#model', '#sunset', '#beach', '#design', '#motivation', '#instamood',
        '#foodporn', '#lifestyle', '#followforfollow', '#sky', '#l4l', '#f4f',
        '#handmade', '#likeforlikes', '#cat',
    ]

    people = list()

    for i in range(number_of_people):    
        new_person = {
            "id": i + 1,
            "name": fake.unique.name(),
        }

        new_tags = get_random_items(tags, 8, 0)

        tag_interactions = dict()
        
        for tag in new_tags:
            tag_interactions[tag] = dict()
                    
            for interaction in ["liked", "posted"]:
                # make some of these tag interactions missing
                if not percent_roll_check(13):
                    continue
                
                tag_interactions[tag][interaction] = random.randint(0, 8)

        new_person["tags"] = tag_interactions

        friends = list()    
        number_of_friends = random.randint(0, 10)
        for i in range(number_of_friends):
            friends.append(random.randint(1, number_of_people))

        # remove the possibility of being friends
        # with oneself, although I do encourage 
        # being your own best friend
        try:
            friends.remove(i)
        except ValueError:
            pass
        
        new_person["friends"] = friends

        people.append(new_person)
    
    return people


def generate_reciprocal_friends(people):
    """
    Is the friendship reciprocal?
    """
    for index, person in enumerate(people):

        person_id = index + 1

        friends = person["friends"]
        
        for friend_id in friends:
            friend_index = friend_id - 1
            if not percent_roll_check(50):
                continue

            friend = people[friend_index]
            if person_id not in friend["friends"]:
                friend["friends"].append(person_id) 
            
            people[friend_index] = friend

    return people


def execute(number_of_people, random_seed, output_path):
    # initialise faker and set our seeds
    fake = Faker()

    Faker.seed(random_seed)
    random.seed(random_seed)

    # make some fake data    
    people = generate_people(fake, number_of_people)
    meta_data = generate_meta_data(fake, len(people), random_seed)
    people = generate_reciprocal_friends(people)

    data = {
        "meta_data": meta_data,
        "data": people,
        }

    with open(output_path, 'w') as outfile:
        json.dump(data, outfile)

    print(json.dumps(meta_data, indent=4))


if __name__ == '__main__':

    # seed for making our random calls reproducable
    RANDOM_SEED = 42

    # how many fake people do we wanna generate?
    NUMBER_OF_PEOPLE = 200

    # where to write out the data
    OUTPUT_PATH = "data.json"

    args_parser = argparse.ArgumentParser(description='Generate fake people data')

    args_parser.add_argument('N',
                       metavar = 'n',
                       type = int,
                       help = 'Number of records to generate',
                       nargs = '?',
                       default = NUMBER_OF_PEOPLE)

    args_parser.add_argument('Seed',
                       metavar = 'seed',
                       type = int,
                       help = 'Seed for random number generation',
                       nargs = '?',
                       default = RANDOM_SEED)


    args_parser.add_argument('Output',
                       metavar = 'output',
                       type = str,
                       help = 'Where to write out the generated data',
                       nargs = '?',
                       default = OUTPUT_PATH)

    args = args_parser.parse_args()    

    execute(args.N, args.Seed, args.Output)