# Predicting flight delays using weather data
This project isn't even remotely finished yet

The end goal is to predict how delayed flights will be based on weather conditions at their departure airport.
Predicting delayed landings based on weather at the destination airport could be done too since that's also included in the dataset I'm using.

## Data Sources
For flight delays I'm using this dataset from the U.S. Department of Transportation:  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;https://www.kaggle.com/datasets/usdot/flight-delays/  
For weather data I doubt there are any premade data sets meeting my exact needs, so I'll likely use some historical weather API such as this one:  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;https://open-meteo.com/en/docs/historical-weather-api.  


flights.csv isn't included in the repo because it's way too large for GitHub.  

## Hypothesis
Worse weather will lead to longer flight delays. "Worse" weather in this situation would be considering factors such as precipitation, wind, and cloud cover.  
Each flight in the delays dataset also includes the IATA airport codes for its origin and destination airports, which can be cross referenced with airports.csv to find the geographic coordinates.  
This will (hopefully) be able to be used with whichever weather API I decide on to get the weather at the time and location of the flight's scheduled departure.
