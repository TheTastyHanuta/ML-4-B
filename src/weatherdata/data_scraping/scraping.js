// ToDo:

// Initial Scraping:
//     File creation
//     File verification
//     Start-time generation: 1 year - 1 Day 0 o'clock
//     52 requests of 168h - hourly


const fs = require("fs")
const axios = require("axios")

// Check if the data dump file exists; if not, create an empty one
if (!fs.existsSync("./scrapedData/scrapedData.json")){
    fs.writeFileSync("./scrapedData/scrapedData.json", "{}");
    console.log("File for the data-dump created!");
}

// Check if the station file exists; if not, abort the script
if (!fs.existsSync("../stationsextraction/stations_extracted copy.json")) {
    console.log("City file not found. Aborting...")
    return;
}

// Load the list of cities and their corresponding IDs
const staedte = JSON.parse(fs.readFileSync("../stationsextraction/stations_extracted copy 2.json", "utf-8"));

// Load previously saved weather data
let datadump =  JSON.parse(fs.readFileSync("./scrapedData/scrapedData.json", "utf-8"));

// Set constants for the API-request
const API_KEY = "1961fb1384d6bcc3fb39acdf228beb96";
const CNT = 168;
let hi = 0;

console.log("Previous data loaded!")
console.log("Data:\n" + JSON.stringify(datadump))

// Main function to perform the data scraping
async function doWork() {
    for (const stadt_name of Object.keys(staedte)) {
        const stadt_id = staedte[stadt_name]
        let start_time = undefined;
        
        // Keep requesting historical data in a loop until an error occurs
        while (true) {
            let shouldBreak = false;

            // Determine the starting time for data retrieval
            if (datadump[stadt_name] && datadump[stadt_name].length > 0) {
                // If data exists yet for this city, use the last recorded timestamp + 1 hour
                start_time = datadump[stadt_name][datadump[stadt_name].length-1].dt+3600
                console.log("Last start time found: " + start_time)
            } else {
                // If no data exists yet for this city, start from the beginning of the year 2025
                
                const temp_start_date = new Date("2025-01-01T00:00:00");
                start_time = Math.floor(temp_start_date.getTime() / 1000);
            
                // const now = new Date()
                // temp_start_time = new Date(now)
                // temp_start_time.setDate(now.getDate()-364);
                // temp_start_time.setDate(now.getDate()-4);
                // temp_start_time.setHours(0, 0, 0, 0)
                //start_time = Math.floor(temp_start_time.getTime()/1000);
                console.log(start_time)
            }

            // Build the request URL for historical weather data
            const request_url = `https://history.openweathermap.org/data/2.5/history/city?id=${stadt_id}&type=hour&start=${start_time}&cnt=${CNT}&appid=${API_KEY}`
            console.log(`Requesting data ${stadt_name} for : ` + start_time)
            hi++;

            // Make the API request
            await axios.get(request_url).then(res => res.data).then(i => {
                // Initialize city´s data array if it doesn´t exist
                if (datadump[stadt_name] == undefined || typeof datadump[stadt_name] != "object") datadump[stadt_name] = []
                // Append the retrieved weather data to the city´s array
                i.list.forEach(weatherelement => datadump[stadt_name].push(weatherelement))
                
                // Log the number of records received and the data of the last one

                // last_transmition_count = i.cnt;
                const last_date = new Date(i.list[i.list.length-1].dt*1000)

                console.log("[" + hi + "] Got " + i.cnt + "/" + CNT + " responses. Last checked date was: " + last_date.toString())
            }).catch(err => {
                // Handle API errors and stop requesting data for this city
                console.error("Error in request: '" + err.message + "'. Skipping to next station...")
                shouldBreak = true;
            })

            if (shouldBreak) break;

            // Wait a second before making the next request 
            await setTimeout(() => {

            }, 1000)
        }
    }
}

// Entry point of the script
async function main() {
    await doWork()
    // console.log(JSON.stringify(datadump))
    // Save the updated data to the JSON file
    fs.writeFileSync("./scrapedData/scrapedData.json", JSON.stringify(datadump, null, 2))
}

main()
