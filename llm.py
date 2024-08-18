from langchain_openai import AzureChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnableLambda
from langchain.schema.output_parser import StrOutputParser
from dotenv import load_dotenv
import json

load_dotenv()

llm = AzureChatOpenAI(azure_deployment="gpt-4o",
                      api_version="2023-03-15-preview")

# ! ||--------------------------------------------------------------------------------||
# ! ||                                 Itinerary Chain                                ||
# ! ||--------------------------------------------------------------------------------||

itinerary_messages = [("system", """
    Context: Assume the user is looking for a personalized travel experience. Consider different aspects like the type of attractions (cultural, adventure, relaxation), preferred accommodation style, dining preferences (local cuisine, fine dining), and budget constraints.
    Your Role: Expert Travel Planner
    Short basic instruction: Create a detailed travel itinerary based on user preferences.
    What you should do: Develop a day-by-day travel itinerary that includes activities, attractions, dining, and accommodations. Use the format where each day has a title and a brief summary of activities for each day in about 100 words. Provide recommendations that fit the user's interests, budget, and preferences.
    Your Goal: Ensure that the generated itinerary is highly customized, thoughtful, and aligns with the user's travel goals. Mention what to eat , where to find those , suggest hotels or accomodation, suggest agency that might help in activities. 
    Result: Return a JSON array of maps here the title is key and the whole day plan is the value

    """),
                      ("human", """
            **My Preferences:**

            - **Full Name:** {full_name}
            - **Country Of Origin:** {country_of_origin}
            - **Occupation:** {occupation}
            - **Main Purpose of Visit:** {main_purpose_of_visit}
            - **Travel Budget:** Nepali Rupees{travel_budget}
            - **Duration Of Visit:** {duration_of_visit}
            - **Food Preferences:** {food_preferences}
            - **Preferred Attractions:** {preferred_attractions}
            - **Number of People Traveling:** {number_of_people_travelling}
            - **Special Activities Interested In:** {special_activities_interested}
            - **Transportation Preferences:** {transportation_preferences}
            - **Accomodation Preferences:** {accommodation_preferences}
            - **Interested Places:** {interested_places}
            - **Weather Preference:** {weather_preference}
            - **Visiting From:** {from_month}
            - **Visiting To:** {to_month}


            Make sure the activities and recommendations are suited to the my preferences and budget."""
                       )]

itinerary_prompt = ChatPromptTemplate.from_messages(itinerary_messages)


def json_decode_array(json_str):
  start_index = json_str.find('[')
  end_index = json_str.rfind(']')

  trimmed_json_str = json_str[start_index:end_index + 1]

  try:
    return json.loads(trimmed_json_str)
  except json.JSONDecodeError as e:
    print(f"Error decoding JSON: {e}")
    return {}


itinerary = RunnableLambda(lambda x: json_decode_array(x))

itinerary_chain = itinerary_prompt | llm | StrOutputParser() | itinerary


def get_itinerary(travel_info: dict) -> list:
  itinerary_result = itinerary_chain.invoke(travel_info)
  return itinerary_result


# ! ||--------------------------------------------------------------------------------||
# ! ||                                 Guideline Chain                                ||
# ! ||--------------------------------------------------------------------------------||

guideline_messages = [
    ("system", """
      You are a travel guide for Nepal. Provide comprehensive advice to tourists on the following format:

      Basic Guidelines and Practices:
        it should be in from an array of strings called Basic Guidelines 
        Describe local customs, cultural practices, and etiquette.
        Include tips on appropriate dress and behavior in public and religious places.

      Emergency Contacts:
        It should be a dictionary called Emergency Contacts where key is the organiztion and value is the contact number
        Provide contact information for local police, medical facilities, tourist assistance, and embassies or consulates.

      Ensure the advice is clear, relevant, and useful for tourists planning their visit to Nepal. give the advice in form of a json.
      """),
    ("human",
     "I am from {country}. What should I be mindful of when I am travelling to nepal"
     ),
]

guideline_prompt = ChatPromptTemplate.from_messages(guideline_messages)


def json_decode_map(json_str):
  start_index = json_str.find('{')
  end_index = json_str.rfind('}')

  trimmed_json_str = json_str[start_index:end_index + 1]

  try:
    return json.loads(trimmed_json_str)
  except json.JSONDecodeError as e:
    print(f"Error decoding JSON: {e}")
    return {}


guidelines = RunnableLambda(lambda x: json_decode_map(x))

guideline_chain = guideline_prompt | llm | StrOutputParser() | guidelines


def get_guidelines(country: str) -> dict:
  guidelines_result = guideline_chain.invoke({"country": country})
  return guidelines_result


def get_all(info):
  it = get_itinerary(info)
  gl = get_guidelines({"country": info["country_of_origin"]})
  return it, gl


if __name__ == "__main__":
  itinerary = get_itinerary({
      "full_name": "Sohil" + "Ansari",
      "country_of_origin": "Russia",
      "occupation": "Data Engineer",
      "main_purpose_of_visit": "explore",
      "travel_budget": "$5000",
      "duration_of_visit": "1month",
      "food_preferences": "Healthy",
      "preferred_attractions": "Tempels",
      "number_of_people_travelling": "2",
      "special_activities_interested": "Rafting",
      "transportation_preferences": "none",
      "accommodation_preferences": "In budget",
      "interested_places": "none",
      "weather_preference": "none",
      "from_month": "November",
      "to_month": "December"
  })

  print(itinerary)
