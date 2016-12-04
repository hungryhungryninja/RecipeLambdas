import boto3
import json

def populate_recipe(input):
    recipe = {
        "name": input.get("name", ""),
        "cookTime": input.get("cookTime", ""),
        "prepTime": input.get("prepTime", ""),
        "cookingMethod": input.get("cookingMethod", ""),
        "nutritionInformation": input.get("nutritionInformation", ""),
        "recipeCategory": input.get("recipeCategory", ""),
        "recipeCuisine": input.get("recipeCuisine", ""),
        "ingredients": input.get("ingredients", []),
        "instructions": input.get("instructions", [])
    }

    # Remove any keys that don't have any values
    recipe_stripped = {}
    for key in recipe:
        if recipe[key] != "":
            recipe_stripped[key] = recipe[key]

    for ingredient in recipe['ingredients']:
        # Check that the ingredient has all of the required fields
        ingredient['name'] = ingredient.get('name', '')
        amount = {}

        if isinstance(ingredient.get('amount'), dict):
            amount['measurement'] = ingredient['amount'].get('measurement', "")
            amount['unitOfMeasure'] = ingredient['amount'].get('unitOfMeasure', "")
            if amount['measurement'] == '':
                amount.pop('measurement')
            if amount['unitOfMeasure'] == '':
                amount.pop('unitOfMeasure')

        ingredient['amount'] = amount

    return recipe_stripped

def get_new_id():
    """
    Retrieves a new key value for the table
    """
    client = boto3.client('lambda')
    response = client.invoke(
        FunctionName='DALNewID',
        InvocationType='RequestResponse',
        Payload=json.dumps({'name': 'Recipes'})
    )

    response = json.loads(response['Payload'].read())
    return response.get('value')

def lambda_handler(input, context):
    """
    API Endpoint for creating Recipes.
    """
    client = boto3.client('lambda')

    input_json = input['body-json']

    recipe = populate_recipe(input_json)

    continue_creating = True
    attempts = 0
    max_attempts = 5

    while continue_creating and attempts < max_attempts:
        # Get the key
        recipe['id'] = get_new_id()

        # Create the create object we'll pass to the lambda endpoint
        create = {
            "table_name": "Recipes",
            "item": recipe
        }

        response = client.invoke(
            FunctionName='DALCreate',
            InvocationType='RequestResponse',
            Payload=json.dumps(create)
        )

        response = json.loads(response['Payload'].read())

        if response.get('status') == 'key_collision':
            continue_creating = True
        else:
            continue_creating = False

        attempts = attempts + 1

        if attempts == max_attempts:
            raise ValueError('Unable to retrieve key value from database for '+
                             'new object')

    return 'recipes/' + str(recipe.get('id'))
