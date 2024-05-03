def concatenate_content(eaac_content_dict: dict) -> str:
    # Initialize an empty string to hold the concatenated content
    concatenated_string = ""

    # Add 'agent_prog' directly since it's a string
    concatenated_string += eaac_content_dict['agent_prog'] + " "

    # Function to handle list types and concatenate each element with a space
    def handle_list(lst):
        return " ".join(lst)

    # Add list fields
    concatenated_string += handle_list(eaac_content_dict['agent_type']) + " "
    concatenated_string += handle_list(eaac_content_dict['role']) + " "
    concatenated_string += handle_list(eaac_content_dict['task']) + " "
    concatenated_string += handle_list(eaac_content_dict['background']) + " "
    concatenated_string += handle_list(eaac_content_dict['urls']) + " "

    # Function to handle dictionary types by converting them into a string
    def handle_dict(dct):
        return " ".join(f"{key}: {value}" for key, value in dct.items())

    # Add 'content' dictionary
    concatenated_string += handle_dict(eaac_content_dict['content']) + " "

    # Strip any leading/trailing whitespace
    concatenated_string = concatenated_string.strip()

    return concatenated_string


