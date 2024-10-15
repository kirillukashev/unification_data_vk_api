import vk_api
import time
import pandas as pd
import difflib
import math

import func_vk
import config


file_path = 'tests/random_row.xlsx'


access_token = '<YOUR TOKEN>'
vk_session = vk_api.VkApi(token=access_token)


def find_school_name_without_num(school_name):
    highest_ratio = 0
    best_match = None

    for candidate in config.schools_without_number:
        matcher = difflib.SequenceMatcher(None, school_name, candidate)
        ratio = matcher.ratio()

        if ratio > highest_ratio:
            highest_ratio = ratio
            best_match = candidate

    return best_match if highest_ratio >= 0.70 else None


def process_value(value):
    if isinstance(value, float) and math.isnan(value):
        return None
    elif isinstance(value, (int, float)):
        return str(int(value))
    else:
        return value


def type_by_school_name(school_name):
    for sample in config.type_inst:
        if sample in school_name:
            return config.type_inst[sample]
    return ''


def process_school_data(vk_session, file_path):
    df = pd.read_excel(file_path)

    results = []
    statuses = []

    for index, row in df.iterrows():
        region_name = process_value(row['region'])
        city_name = process_value(row['location_name'])
        school_name = process_value(row['names'])
        school_number = process_value(row['school_number'])
        other_answer = process_value(row['abbreviated'])

        if region_name and 'моск' in region_name.lower():
            region_name = 'Московская обл'
            city_name = 'Москва'

        if region_name and 'санкт' in region_name.lower():
            region_name = 'Ленинградская обл'
            city_name = 'Санкт-Петербург'

        if region_name and not city_name:
            city_name = config.region_to_capital.get(region_name, None)
            if city_name in config.fixed_city_names:
                city_name = config.fixed_city_names.get(city_name, None)

        if city_name in config.fixed_city_names:
            city_name = config.fixed_city_names[city_name]
        # print()
        # print(region_name, city_name, school_name, school_number, sep=' | ')
        if region_name and school_name:
            try:
                school_result = func_vk.get_school_by_data(vk_session, region_name, city_name, school_name.lower())
                if school_result:
                    results.append(school_result[1])
                    statuses.append("accepted: from_database_vk_by_school_name")
                elif school_number:
                    # type_of_inst = type_by_school_name(school_name)
                    type_of_inst = ''
                    school_result = func_vk.get_school_by_data(vk_session, region_name, city_name, type_of_inst + school_number)
                    if school_result:
                        results.append(school_result[1])
                        statuses.append("from_database_vk_by_school_number")
                    else:
                        results.append(other_answer)
                        statuses.append("from_other_result_table")
                elif find_school_name_without_num(school_name):
                    results.append(find_school_name_without_num(school_name))
                    statuses.append("accepted: from_schools_without_number")
                else:
                    results.append(other_answer)
                    statuses.append("from_other_result_table")

            except Exception as e:
                results.append(other_answer)
                statuses.append(f"error: {str(e)}, from_other_result_table")

        elif not region_name or school_name:
            results.append(other_answer)
            statuses.append("from_other_result_table")
        elif not school_name:
            results.append(other_answer)
            statuses.append(f"school_name not specified, from_other_result_table")

    df['result'] = results
    df['status'] = statuses

    output_file_path = file_path.replace('.xlsx', '_results.xlsx')
    df.to_excel(output_file_path, index=False)

    print(f"Processed file saved as {output_file_path}")

process_school_data(vk_session, file_path)
