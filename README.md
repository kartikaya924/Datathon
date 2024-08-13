# Datathon
Love’s Travel Stops aimed to optimize its replenishment strategy for Anti-Gel diesel additives due to the challenges posed by seasonal sales fluctuations. The objective was to balance inventory levels to avoid overstocking, which could negatively impact the balance sheet, and understocking, which could lead to missed sales opportunities.

## Problem Summary & Purpose of the Analysis 

We have been asked to optimize Love’s Travel Stops replenishment strategy for Anti-Gel diesel additives. Because of the seasonality of Anti-Gel sales, it can be hard to predict the stock needed for a store. Overstocking can negatively affect the balance sheet, but understocking can lead to missed sales opportunities.  

## Data and Methods Used 

We have developed a dynamic ordering system for Loves stores based on historical sales data and external factors. The model takes user inputs for store code and date, filters the relevant data, and then calculates suggested order quantities for each product, considering a combination of store-specific features and external variables. The suggested order is determined by a weighted average of factors such as store region, store tier, loyalty units, distance to distribution center, and the minimum temperature forecasted for the upcoming week (using an external API). To enhance its accuracy, the model incorporates a normalization process and an error term, which considers the variability in the past year’s sales for each product. The resulting suggested orders are presented in two views: one based on the past year's performance, and another determined by a threat threshold. The application aims to provide an intuitive tool for optimizing inventory management and assisting decision-makers for Love’s. 

1. Data

The dataset used is Datathon Dataset.xlsx, which includes historical sales data along with various attributes related to stores and products. The key columns utilized are:

	•	SalesDate: Date of the sale
	•	StoreNumber: Identifier for each store
	•	ProductDescription: Description of the product
	•	Units: Number of units sold
	•	RegionName: Name of the region where the store is located
	•	StoreTierTypeDescription: Description of the store tier
	•	UnitsLoyalty: Loyalty units sold
	•	DCDistance: Distance from the distribution center
	•	Latitude: Latitude of the store location
	•	Longitude: Longitude of the store location
	•	LeadTime: Time required to replenish the stock

2. Data Preprocessing

	1.	Feature Engineering:
	•	RegionBinary: Encodes regions as 0 or 1 based on the RegionName. Stores starting with ‘C’ are assigned 0; others are assigned 1.
	•	StoreTierEncoded: Encodes the StoreTierTypeDescription using Label Encoding.
	2.	Weather Data:
	•	The process_weather_data function fetches historical weather data for a given latitude and longitude using the Open-Meteo API. It calculates the minimum temperature for the next week, which is used to adjust order quantities.

3. Model and Calculations

	1.	User Input:
    
	•	Users provide a store code and a date. The application filters the dataset based on these inputs to select relevant data for analysis.

	3.	Weighted Average Calculation:
    
	•	Weights are applied to various features to calculate a WeightedAverage score for each product at the specified store:
	•	RegionBinary: Encoded as 0 or 1
	•	StoreTierEncoded: Encoded store tier
	•	UnitsLoyalty: Number of loyalty units sold
	•	DCDistance: Distance from the distribution center
	•	Temperature: Minimum temperature forecast for the upcoming week

The formula used for calculating WeightedAverage is:

\text{WeightedAverage} = w_{\text{store region}} \times \text{RegionBinary} - w_{\text{store tier}} \times \text{StoreTierEncoded} + w_{\text{store profit}} \times \text{UnitsLoyalty} - w_{\text{dc dist}} \times \text{DCDistance} - w_{\text{store low temp}} \times \text{Temperature}

### where each weight ( w_{\text{store region}}, w_{\text{store tier}}, \ldots ) is set to 0.2.

	3.	Normalization and Error Term:
 
	•	The WeightedAverage values are normalized using MinMaxScaler.
	•	An error_term is calculated to account for variability in past sales and lead times:

\text{error_term} = \text{NormalizedValue} \times \sqrt{\text{LeadTime} \times \text{std\_units\_by\_store}}

	4.	Suggested Order Calculation:
	•	The suggested order is computed using:

\text{suggested\_order} = (\text{mean\_units} \times \text{LeadTime}) - \text{error_term}

	•	This value is floored to the nearest integer.
 
	5.	Handling Non-Matching Products:
 
	•	For products not matching the filtered data, suggested orders are calculated as:

\text{suggested\_order} = \text{mean\_units} \times \text{LeadTime} + 3

	•	This ensures a baseline order quantity for products not present in the filtered dataset.

Results and Recommendations

	•	Suggested Orders Based on Past Year:
	•	Orders are suggested based on historical data for each product at the specified store.
	•	Suggested Orders Based on Threat Threshold:
	•	Orders are suggested for products not present in the filtered data to ensure adequate stock levels.
	•	Aggregate Difference:
	•	The application calculates and displays the difference between the total units suggested based on past data and the total units suggested for non-matching products.

We dove into store performance by measuring a couple of different metrics: average days in inventory, gross margin returns on investment in inventory, and the inventory-to-sales ratio. We normalized each metric then created an equally weighted scoring metric to find the top and bottom performing stores.  

## Results and Interpretation 

We found that temperature had the most effect on both profit margins and sell-through by using a correlation matrix. We also found that C-stores had less sales, this is due to their target demographic being families rather than truckers, which is reflected in the loyalty sales percentages. This is because only truckers can join the loyalty program. 

## Recommendations & Conclusions 

To optimize Love’s current strategy, our model looks at past year sales in relation to time of year, temperature, distance from a distribution center, lead time, store tier, and profitability. By using this model stores will be able to optimize inventory replenishment strategy. We also recommend opening a distribution center in the north as these are the most successful stores in terms of profitability and sell-through. 
