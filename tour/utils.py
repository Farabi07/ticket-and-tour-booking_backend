import requests   
def sync_cms_tour_content(self):
        """
        Fetch available dates from the external API and update TourContent instance
        only if TourContent.name matches Bus.name EXACTLY.
        """
        if not self.name:  
            print("⚠️ TourContent has no name, skipping sync.")
            return  

        # Step 1: Fetch all buses from the external API
        bus_api_url = "http://192.168.68.123:8000/bus/api/v1/bus/all/"
        print(f"🔍 Fetching all buses from: {bus_api_url}")  

        try:
            response = requests.get(bus_api_url, timeout=10)
            response.raise_for_status()  
            buses = response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching bus list: {e}")
            return  

        # Step 2: Find the matching bus (EXACT MATCH)
        bus_id = next((bus["id"] for bus in buses if bus.get("name") == self.name), None)

        if not bus_id:
            print(f"❌ No matching Bus found for TourContent: '{self.name}'")
            return  

        print(f"✅ Matched Bus ID: {bus_id} for TourContent: '{self.name}'")

        # Step 3: Fetch available dates for the matched bus
        external_url = f"http://192.168.68.123:8000/bus/api/v1/bus/{bus_id}"
        print(f"🔄 Fetching bus data from: {external_url}")  

        try:
            response = requests.get(external_url, timeout=10)
            print(f"📌 Response Status Code: {response.status_code}")  
            print(f"📌 Response Content: {response.text}")  

            if response.status_code == 200:
                data = response.json()
                available_dates = data.get("available_dates", [])
                print(f"📅 Available Dates for Bus {bus_id}: {available_dates}")

                # If you want to store available_dates in TourContent, do this:
                # self.available_dates = available_dates  # Assuming available_dates field exists
                # self.save()  # Save changes
            else:
                print(f"⚠️ Unexpected Response: {response.status_code}")

        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching bus details: {e}")
