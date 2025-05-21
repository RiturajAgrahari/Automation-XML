import xml.etree.ElementTree as ET
import base64
import os


def encode_image_to_base64(
        image_path: str = 'scenery.png'
):
    """
    This function converts the image into base64 utf-8 encoded string.

    :param image_path: Path of the image.

    :return: Returns base64encoded image string.
    """
    try:
        # Opening the image and encoding it
        with open(image_path, 'rb') as image_file:

            # Encoding the image into string.
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')

            # Returning the encoded string.
            return encoded_string

    # If image doesn't found.
    except FileNotFoundError:
        print(f"Error: Image file not found at {image_path}")
        return None

    # Handling exception.
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def create_xml_file(
        filename: str = 'image.xml',
        root_name: str = 'root',
        elements_data: list[dict] = None
):
    """
    This function creates an XML file with the specified filename, root element, and data.

    :param filename:str The name of the XML file to create (e.g., "data.xml").
    :param root_name:str The name of the root element (e.g., "root", "data").
    :param elements_data:list[dict] A list of dictionaries, where each dictionary
            represents an element and its sub-elements/attributes.  Each dictionary
            should have the following structure:
            {
                'tag': 'element_name',  # Required: Tag name of the element
                'attributes': {'attr1': 'value1', 'attr2': 'value2', ...}, # Optional
                'text': 'element_text',      # Optional: Text content of the element
                'children': [              # Optional: List of child elements (dictionaries)
                    {...},  # Child element 1
                    {...},  # Child element 2
                    ...
                ]
            }

    :return: Creates an XML file.
    """
    if elements_data is None:
        elements_data = [{'tag': 'element'}]
    try:
        # 1. Create the root element
        root = ET.Element(root_name)

        # 2. Create elements and sub-elements recursively
        def _add_element(parent, element_data):
            """Recursive helper function to add elements and sub-elements."""
            tag = element_data.get('tag')
            if not tag:
                print("Warning: 'tag' is missing in element data. Skipping.")
                return None  # Skip if tag is missing to avoid errors

            element = ET.SubElement(parent, tag)

            attributes = element_data.get('attributes', {})  # Default to {} if missing
            for attr, value in attributes.items():
                element.set(attr, value)

            text = element_data.get('text')
            if text is not None:  # Check for None explicitly
                element.text = text

            children = element_data.get('children', [])  # Default to [] if missing
            for child_data in children:
                _add_element(element, child_data)  # Recursive call

            return element  # Return the created element

        for element_data in elements_data:
            _add_element(root, element_data)

        # 3. Create an ElementTree object
        tree = ET.ElementTree(root)

        # 4. Write the XML to a file
        #    Use 'utf-8' encoding explicitly.  Use xml_declaration=True to get a header.
        tree.write(filename, encoding='utf-8', xml_declaration=True)

        print(f"Successfully created XML file: {filename}")

    except Exception as e:
        print(f"An error occurred while creating the XML file: {e}")
        return False  # Indicate failure

    return True  # Indicate success


def convert_xml_images(xml_file_path):
    try:
        tree = ET.parse(xml_file_path)
        root = tree.getroot()
        print(f'[0]-- {root.tag}')
        image_index = 0
        for level_1_child in root:
            print(f'[1]---- {level_1_child.tag}  --> {level_1_child.attrib}')
            for level_2_child in level_1_child:
                print(f'[2]---- {level_2_child.tag}  --> {level_2_child.attrib}')
                if len(level_2_child.text) > 100:
                    print(f'Downloading image [{image_index}]...')
                    save_base64_to_image(level_2_child.text, f"extracted_image{image_index}.jpg")
                    image_index += 1

    except Exception as e:
        print(e)


def save_base64_to_image(base64_string, image_filename="extracted_image.jpg"):
    try:
        output_folder = "extracted_images"
        os.makedirs(output_folder, exist_ok=True)
        # image_filename = "extracted_image.jpg"
        output_file_path = os.path.join(output_folder, image_filename)

        # Decode the Base64 string
        image_data = base64.b64decode(base64_string)

        # Write the binary data to the image file
        with open(output_file_path, 'wb') as f:
            f.write(image_data)

        print(f"Successfully saved image to: {output_file_path}")

    except base64.binascii.Error as e:
        print(f"Error decoding Base64 data: {e}")
    except Exception as e:
        print(f"An error occurred while saving the image: {e}")


if __name__ == "__main__":
    # Encoding the image.
    image_file = "scenery.png"
    base64_string = encode_image_to_base64(image_file)

    # Creating a XML file for the encoded image
    my_xml_data = [
        {
            'tag': 'root',
            'attributes': {'version': '1.0', 'encoding': 'UTF-8'},  # Attributes for root
            'children': [
                {
                    'tag': 'image_title',
                    'attributes': {'id': '1', 'type': 'image'},
                    'text': f'{image_file}.',
                    'children': []
                },
                {
                    'tag': 'image_string',
                    'attributes': {'id': '2', 'type': 'binary'},
                    'text': f'{base64_string}',
                    'children': []
                },
                {
                    'tag': 'end_tag',
                }
            ]
        },
    ]

    # Create the XML file
    if create_xml_file(
            filename="image.xml",
            root_name="root",
            elements_data=my_xml_data
    ):
        print(f"XML file has been created successfully.")
    else:
        print(f"Failed to create XML file.")

    # Fetching decoding and storing the image
    xml_file = "image.xml"
    convert_xml_images(xml_file)
