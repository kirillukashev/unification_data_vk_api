import vk_api


def get_regions(vk_session, q, country_id, need_all=True, count=1, offset=0):
    vk = vk_session.get_api()

    try:
        response = vk.database.getRegions(
            country_id=country_id,
            q=q,
            need_all=int(need_all),
            count=count,
            offset=offset
        )
        return response['items']
    except vk_api.exceptions.ApiError as error:
        print(f'An error occurred: {error}')
        return []


def get_cities(vk_session, q, country_id, region_id=None, need_all=True, count=1, offset=0):
    vk = vk_session.get_api()

    try:
        response = vk.database.getCities(
            country_id=country_id,
            q=q,
            region_id=region_id,
            need_all=int(need_all),
            count=count,
            offset=offset
        )
        return response['items']
    except vk_api.exceptions.ApiError as error:
        print(f'An error occurred: {error}')
        return []


def get_schools(vk_session, city_id, q, count=1, offset=0):
    vk = vk_session.get_api()

    try:
        response = vk.database.getSchools(
            city_id=city_id,
            q=q,
            count=count,
            offset=offset
        )
        return response['items']
    except vk_api.exceptions.ApiError as error:
        print(f'An error occurred: {error}')
        return []


def get_school_by_data(vk_session,  region_name, city_name, school_name):
    country_id = 1

    regions = get_regions(vk_session, region_name, country_id)

    if not regions or len(regions) == 0:
        return None

    our_region = regions[0]
    region_id = our_region["id"]

    cities = get_cities(vk_session, city_name, country_id, region_id)

    if not cities or len(cities) == 0:
        return None

    our_city = cities[0]


    city_id = our_city["id"]

    if not schools or len(schools) == 0:
        return None

    our_school = schools[0]

    return (our_school["id"], our_school["title"])
