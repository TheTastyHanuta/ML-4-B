// ToDo:

// Initial Scraping:
//     File creation
//     File verification
//     Start-time generation: 1 year - 1 Day 0 o'clock
//     52 requests of 168h - hourly

const fs = require("fs")
const axios = require("axios")

if (!fs.existsSync("./scrapedData/scrapedData.json")){
    fs.writeFileSync("./scrapedData/scrapedData.json", "{}");
    console.log("File for the data-dump created!");
}

if (!fs.existsSync("../stationsextraction/stations_extracted copy.json")) {
    console.log("City file not found. Aborting...")
    return;
}

const staedte = JSON.parse(fs.readFileSync("../stationsextraction/stations_extracted copy.json", "utf-8"));
let datadump =  JSON.parse(fs.readFileSync("./scrapedData/scrapedData.json", "utf-8"));
const API_KEY = "1961fb1384d6bcc3fb39acdf228beb96";
const CNT = 168;
let hi = 0;

console.log("Previous data loaded!")
console.log("Data:\n" + JSON.stringify(datadump))

async function doWork() {
    for (const stadt_name of Object.keys(staedte)) {
        const stadt_id = staedte[stadt_name]
        let start_time = undefined;
        
        while (true) {
            let shouldBreak = false;
            if (datadump[stadt_name] && datadump[stadt_name].length > 0) {
                start_time = datadump[stadt_name][datadump[stadt_name].length-1].dt+3600
                console.log("Last start time found: " + start_time)
            } else {
                const now = new Date()
                temp_start_time = new Date(now)
                temp_start_time.setDate(now.getDate()-364);
                // temp_start_time.setDate(now.getDate()-4);
                temp_start_time.setHours(0, 0, 0, 0)
                start_time = Math.floor(temp_start_time.getTime()/1000);
                // console.log(start_time)
            }

            const request_url = `https://history.openweathermap.org/data/2.5/history/city?id=${stadt_id}&type=hour&start=${start_time}&cnt=${CNT}&appid=${API_KEY}`
            console.log(`Requesting data ${stadt_name} for : ` + start_time)
            hi++;

            await axios.get(request_url).then(res => res.data).then(i => {
                if (datadump[stadt_name] == undefined || typeof datadump[stadt_name] != "object") datadump[stadt_name] = []
                i.list.forEach(weatherelement => datadump[stadt_name].push(weatherelement))
                
                // last_transmition_count = i.cnt;
                const last_date = new Date(i.list[i.list.length-1].dt*1000)

                console.log("[" + hi + "] Got " + i.cnt + "/" + CNT + " responses. Last checked date was: " + last_date.toString())
            }).catch(err => {
                console.error("Error in request: '" + err.message + "'. Skipping to next station...")
                shouldBreak = true;
            })

            if (shouldBreak) break;

            await setTimeout(() => {

            }, 1000)
        }
    }
}

async function main() {
    await doWork()
    // console.log(JSON.stringify(datadump))
    fs.writeFileSync("./scrapedData/scrapedData.json", JSON.stringify(datadump, null, 2))
}

main()
