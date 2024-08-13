import streamlit as st
import pandas as pd
import datetime
from PIL import Image
from sklearn.preprocessing import MinMaxScaler
import requests_cache
import openmeteo_requests
from retry_requests import retry
import numpy as np
from sklearn.preprocessing import LabelEncoder


scaler = MinMaxScaler()
def process_weather_data(latitude, longitude, start_date):
    # Setup the Open-Meteo API client with cache and retry on error
    cache_session = requests_cache.CachedSession('.cache', expire_after=-1)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)

    # Define end_date as 7 days after start_date
    end_date = start_date + pd.Timedelta(days=7)

    # Define parameters for API request
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date.strftime('%Y-%m-%d'),
        "end_date": end_date.strftime('%Y-%m-%d'),
        "hourly": "temperature_2m",
        "temperature_unit": "fahrenheit"
    }

    # Make API request
    responses = openmeteo.weather_api(url, params=params)

    # Process first location. Add a for-loop for multiple locations or weather models
    response = responses[0]

    # Process hourly data. The order of variables needs to be the same as requested.
    hourly = response.Hourly()
    hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()

    # Extract the minimum temperature for the next week
    min_temp_for_next_week = min(hourly_temperature_2m[-7:])

    return min_temp_for_next_week

df = pd.read_excel('Datathon Dataset.xlsx')
df['RegionBinary'] = df['RegionName'].apply(lambda x: 0 if x.startswith('C') else 1)
df['StoreTierEncoded'] = LabelEncoder().fit_transform(df['StoreTierTypeDescription'])

def main():
    # Load your dataset (replace 'Datathon Dataset.xlsx' with the correct path)


    with st.sidebar:
        store_code = st.text_input("Type Store Code")
        date = st.text_input("Input Date")

        submit_button = st.button("Submit")

    if submit_button:
        # Filter data based on store_code and date
        storeNumber = int(store_code)  # Assuming store_code is an integer
        sales_date = pd.to_datetime(date)

        df_filter_code = df[(df['SalesDate'] >= sales_date) & (df['SalesDate'] < sales_date + pd.Timedelta(days=7)) & (df['StoreNumber'] == storeNumber)]

        result = df_filter_code.groupby('ProductDescription')['Units'].sum()

        df_not_matching = df[
            ~df['ProductDescription'].isin(df_filter_code['ProductDescription']) & ~df['ProductDescription'].isin(
                df_filter_code['ProductDescription'])]

        w_store_tier = 0.2
        w_store_region = 0.2
        w_store_low_temp = 0.2
        w_store_profit = 0.2
        w_dc_dist = 0.2



        df_filter_code['WeightedAverage'] = (
                w_store_region * df_filter_code['RegionBinary'] - w_store_tier * df_filter_code['StoreTierEncoded'] +
                w_store_profit * df_filter_code['UnitsLoyalty'] -
                w_dc_dist * df_filter_code['DCDistance'] -
                w_store_low_temp * (
                    process_weather_data(df_filter_code['Latitude'], df_filter_code['Longitude'], sales_date))
        )



        column_to_normalize = df_filter_code['WeightedAverage'].values.reshape(-1, 1)

        # Fit and transform the data
        df_filter_code['NormalizedValue'] = scaler.fit_transform(column_to_normalize)

        # Calculate the standard deviation of 'Units' and 'LeadTime' for each store
        df_filter_code['std_units_by_store'] = df_filter_code.groupby('ProductDescription')['Units'].transform(
            'std').fillna(0)

        # Calculate the error term with square root
        df_filter_code['error_term'] = df_filter_code['NormalizedValue'] * (
            np.sqrt(df_filter_code['LeadTime'] * df_filter_code['std_units_by_store']))


        df_filter_code['suggested_order'] = df_filter_code.groupby('ProductDescription')['Units'].transform('mean') * \
                                            df_filter_code['LeadTime'] - df_filter_code['error_term']

        df_filter_code['suggested_order'] = np.floor(df_filter_code['suggested_order'])

        df_filter_code.groupby('ProductDescription')['suggested_order'].sum()

        grouped_df = df_filter_code.groupby('ProductDescription')['suggested_order'].sum().reset_index()

        df_not_matching['suggested_order'] = np.floor(
            df_not_matching.groupby('ProductDescription')['Units'].transform('mean') * df_not_matching['LeadTime']) + 3

        # df_not_matching['suggested_order']

        add_df = df_not_matching.groupby('ProductDescription')['suggested_order'].mean().reset_index()

        add_df['suggested_order'] = np.floor(add_df['suggested_order'])


        # Display or use the result_df as needed
        st.write("Suggested Orders Based On Past Year")
        st.write(grouped_df)

        st.write("Suggested Orders Based On Threat Threshold")
        st.write(add_df)

        st.write("Aggregate Difference :", abs(pd.DataFrame(result)['Units'].sum() - grouped_df['suggested_order'].sum()))

if __name__ == "__main__":
    main()
