// ToDo:

// Initial Scraping:
//     File creation
//     File verification
//     Start-time generation: 1 year - 1 Day 0 o'clock
//     52 requests of 168h - hourly

const fs = require("fs")

if (!fs.existsSync("./scrapedData/scrapedData.json")){
    fs.writeFileSync("./scrapedData/scrapedData.json", "{}");
    console.log("File for the data-dump created!");
}

const staedte = {};
let datadump =  {};

datadump = JSON.parse(fs.readFileSync("./scrapedData/scrapedData.json", "utf-8"));
console.log("Previous data loaded!")
console.log("Data:\n" + JSON.stringify(datadump))

for (const stadt_name in Object.keys(staedte)) {
    const stadt_id = staedte[stadt_name]

    

}