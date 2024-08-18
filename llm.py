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

    Here is an estimated price range for the treks you listed:

    1-Day Treks:
    Bandipur to Ramkot Hike: Approximately NPR 3,700-4,900 per person for a guided tour, including transportation from Kathmandu.
    Gorkha Durbar Hike: Similar to Bandipur, the cost for a day hike, including transportation, could range from NPR 3,000-5,000.
    Chitwan National Park Jungle Walk: Prices vary depending on the package but typically range from NPR 2,000-4,000 per person.
    Lumbini Heritage Site Walk: Around NPR 2,500-4,000 per person, depending on guide services and transportation.
    2-Day Treks:
    Nagarkot to Dhulikhel Hike: Estimated cost is around NPR 8,000-10,000 per person, including accommodation and meals.
    Bhaktapur to Panauti Hike: This trek might cost around NPR 7,000-9,000 per person.
    Dhulikhel to Namobuddha Hike: Costs are similar, ranging from NPR 7,000-10,000 per person.
    Multi-Day Treks:
    Everest Base Camp Trek (12-14 days): The cost is typically around $1,000-3,000 USD depending on services included.
    Gokyo Lakes Trek (10-12 days): Approximately $1,200-2,500 USD.
    Three Passes Trek (17-21 days): Estimated at $1,500-3,500 USD.
    Annapurna Base Camp Trek (7-10 days): Around $800-1,500 USD.
    Annapurna Circuit Trek (14-21 days): Estimated between $1,000-2,500 USD.
    Mardi Himal Trek (5-7 days): Costs around $500-1,000 USD.
    Langtang Valley Trek (5-7 days): Estimated at $500-1,200 USD.
    Gosaikunda Trek (6-8 days): Around $600-1,300 USD.
    Helambu Trek (5-7 days): Estimated at $500-1,000 USD.
    Manaslu Circuit Trek (12-14 days): Costs range from $1,200-2,500 USD.
    Tsum Valley Trek (10-12 days): Around $1,200-2,000 USD.
    Upper Mustang Trek (10-14 days): Costs between $1,500-3,000 USD.
    Lower Mustang Trek (5-7 days): Estimated at $700-1,500 USD.
    Upper Dolpo Trek (18-21 days): Costs range from $2,500-4,500 USD.
    Lower Dolpo Trek (10-12 days): Estimated at $1,500-3,000 USD.
    Kanchenjunga Base Camp Trek (18-21 days): Around $2,500-4,000 USD.
    Kanchenjunga North Base Camp Trek (15-18 days): Similar costs, around $2,000-3,500 USD.
    Rara Lake Trek (7-10 days): Approximately $800-1,500 USD.

    Average cost of hotel in Nepal is about Rs 2500 per night

    Average cost of special activities:
    White Water Rafting: Costs range from $50-$150 per person, depending on the river and duration​.
    Paragliding in Pokhara: Around $80-$120 per person for a 30-minute flight.
    Jungle Safari in Chitwan National Park: Approximately $100-$150 per person for a full-day experience.
    Mountain Flights: Costs range from $200-$300 per person for a scenic flight over the Himalayas.
    Bungee Jumping: Approximately $80-$120 per jump.
    Helicopter Tour: Costs vary significantly based on the destination. For example, an Everest Base Camp helicopter tour can range from $1,200-$2,500 per person, while other destinations like Annapurna or Langtang can be slightly lower.

    """),
                      ("human", """
            **My Preferences:**

            - **Full Name:** {full_name}
            - **Country Of Origin:** {country_of_origin}
            - **Occupation:** {occupation}
            - **Main Purpose of Visit:** {main_purpose_of_visit}
            - **Travel Budget:** {travel_budget} of {country_of_origin}'s currency
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
