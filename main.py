from fastapi import FastAPI, HTTPException, Request, Form
from pydantic import ValidationError
from llm import get_all
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError
from typing import List


def parse_comma_separated(value: str):
  return [item.strip() for item in value.split(",") if item.strip()]


def validate_form(data: dict):

  # Validate required string fields
  if not data["first_name"] or not data["first_name"].strip():
    raise ValidationError("First Name is required.")
  if not data["last_name"] or not data["last_name"].strip():
    raise ValidationError("Last Name is required.")
  if not data["country_of_origin"] or not data["country_of_origin"].strip():
    raise ValidationError("Country of Origin is required.")
  if not data["occupation"] or not data["occupation"].strip():
    raise ValidationError("Occupation is required.")
  if not data["main_purpose_of_visit"] or not data[
      "main_purpose_of_visit"].strip():
    raise ValidationError("Main Purpose of Visit is required.")
  if not data["transportation_preferences"] or not data[
      "transportation_preferences"].strip():
    raise ValidationError("Transportation Preferences is required.")
  if not data["accommodation_preferences"] or not data[
      "accommodation_preferences"].strip():
    raise ValidationError("Accommodation Preferences is required.")
  if not data["weather_preference"] or not data["weather_preference"].strip():
    raise ValidationError("Weather Preference is required.")
  if not data["from_month"] or not data["from_month"].strip():
    raise ValidationError("From Month is required.")
  if not data["to_month"] or not data["to_month"].strip():
    raise ValidationError("To Month is required.")

  # Validate numeric fields
  if data["travel_budget"] <= 0:
    raise ValidationError("Travel Budget must be a positive integer.")
  if data["duration_of_visit"] <= 0:
    raise ValidationError("Duration of Visit must be a positive integer.")
  if data["number_of_people_travelling"] <= 0:
    raise ValidationError(
        "Number of People Travelling must be a positive integer.")

  # Validate lists for non-empty values
  def validate_list_field(field_name: str, field_list: List[str]):
    if not field_list:
      raise ValidationError(f"{field_name} should not be empty.")
    elif any(not item.strip() for item in field_list):
      raise ValidationError(f"{field_name} contains empty entries.")

  validate_list_field("Food Preferences", data["food_preferences_list"])
  validate_list_field("Preferred Attractions",
                      data["preferred_attractions_list"])
  validate_list_field("Special Activities Interested",
                      data["special_activities_interested_list"])
  validate_list_field("Interested Places", data["interested_places_list"])


app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


@app.get("/")
async def root(request: Request, response_class=HTMLResponse):
  return templates.TemplateResponse(
      request=request,
      name="index.html",
  )


@app.get("/itinerary/create", response_class=HTMLResponse)
async def create_itinerary(request: Request):
  return templates.TemplateResponse(request=request,
                                    name="create-itinerary.html")


@app.get("/itinerary", response_model=dict)
def get_itinerary(request: Request, first_name: str, last_name: str,
                  country_of_origin: str, occupation: str,
                  main_purpose_of_visit: str, travel_budget: int,
                  duration_of_visit: int, food_preferences: str,
                  preferred_attractions: str, number_of_people_travelling: int,
                  special_activities_interested: str,
                  transportation_preferences: str,
                  accommodation_preferences: str, interested_places: str,
                  weather_preference: str, from_month: str, to_month: str):

  food_preferences_list = parse_comma_separated(food_preferences)
  preferred_attractions_list = parse_comma_separated(preferred_attractions)
  special_activities_interested_list = parse_comma_separated(
      special_activities_interested)
  interested_places_list = parse_comma_separated(interested_places)
  form_data = {
      "request": request,
      "first_name": first_name,
      "last_name": last_name,
      "country_of_origin": country_of_origin,
      "occupation": occupation,
      "main_purpose_of_visit": main_purpose_of_visit,
      "travel_budget": travel_budget,
      "duration_of_visit": duration_of_visit,
      "food_preferences_list": food_preferences_list,
      "preferred_attractions_list": preferred_attractions_list,
      "number_of_people_travelling": number_of_people_travelling,
      "special_activities_interested_list": special_activities_interested_list,
      "transportation_preferences": transportation_preferences,
      "accommodation_preferences": accommodation_preferences,
      "interested_places_list": interested_places_list,
      "weather_preference": weather_preference,
      "from_month": from_month,
      "to_month": to_month
  }

  it, gl = get_all({
      "full_name":
      form_data["first_name"] + " " + form_data["last_name"],
      "country_of_origin":
      form_data["country_of_origin"],
      "occupation":
      form_data["occupation"],
      "main_purpose_of_visit":
      form_data["main_purpose_of_visit"],
      "travel_budget":
      form_data["travel_budget"],
      "duration_of_visit":
      form_data["duration_of_visit"],
      "food_preferences":
      form_data["food_preferences_list"],
      "preferred_attractions":
      form_data["preferred_attractions_list"],
      "number_of_people_travelling":
      form_data["number_of_people_travelling"],
      "special_activities_interested":
      form_data["special_activities_interested_list"],
      "transportation_preferences":
      form_data["transportation_preferences"],
      "accommodation_preferences":
      form_data["accommodation_preferences"],
      "interested_places":
      form_data["interested_places_list"],
      "weather_preference":
      form_data["weather_preference"],
      "from_month":
      form_data["from_month"],
      "to_month":
      form_data["to_month"]
  })
  return templates.TemplateResponse(request=request,
                                    name="show-itinerary.html",
                                    context={
                                        "it": it,
                                        "gl": gl
                                    })


if __name__ == "__main__":
  import uvicorn
  uvicorn.run(app, host="127.0.0.1", port=8080)
