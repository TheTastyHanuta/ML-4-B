const fs = require('fs');

// Load the original JSON file
const originalData = fs.readFileSync("./scrapedData/scrapedData.json"); // Replace with your file name

// Get entries as [key, value] pairs
const entries = Object.entries(originalData);

// Calculate the midpoint
const mid = Math.ceil(entries.length / 2);

// Split the entries into two halves
const firstHalf = Object.fromEntries(entries.slice(0, mid));
const secondHalf = Object.fromEntries(entries.slice(mid));

// Write the halves to separate files
fs.writeFileSync('data_part1.json', JSON.stringify(firstHalf, null, 2));
fs.writeFileSync('data_part2.json', JSON.stringify(secondHalf, null, 2));

console.log('Split complete: data_part1.json and data_part2.json created.');
