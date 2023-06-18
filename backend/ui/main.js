/**
 * Create a graph from the given temp and humidity data.
 * 
 * @param {HTMLElement} parent 
 * @param {string} name
 * @param {number[]} temp 
 * @param {number[]} humidity 
 */
function createGraph(parent, name, temp, hum) {
    const section = document.createElement("section")
    const heading = document.createElement("h2")
    const canvas = document.createElement("canvas")

    heading.innerText = name

    section.append(heading)
    section.append(canvas)
    parent.append(section)

    new Chart(canvas, {
        type: 'line',
        data: {
            datasets: [
                {
                    label: "Temperature",
                    yAxisID: "temp",
                    data: temp,
                },
                {
                    label: "Humidity",
                    yAxisID: "hum",
                    data: hum,
                },
            ],
        },
        options: {
            datasets: {
                line: {
                    pointStyle: false,
                },
            },
            scales: {
                x: {
                    type: 'time',
                    time: {
                        isoWeekday: true,
                        tooltipFormat: "yyyy-MM-dd HH:mm:ss",
                        displayFormats: {
                            second: "mm:ss",
                            minute: "HH:mm",
                            hour: "HH:mm",
                            day: "yyyy-MM-dd",
                            week: "yyyy-MM-dd",
                            month: "yyyy-MM-dd",
                            year: "yyyy",
                        },
                    }
                },
                temp: {
                    type: 'linear',
                    min: -25,
                    max: 55,
                    title: {
                        display: true,
                        text: "Celsius",
                        align: "end",
                    },
                    position: 'right',
                },
                hum: {
                    type: 'linear',
                    min: 0,
                    max: 100,
                    title: {
                        display: true,
                        text: "% RH",
                        align: "end",
                    },
                    position: 'left',
                }
            }
        }
    });
}

/**
 * Split a single list of measurement data into two separate lists.
 * 
 * @param {{timestamp: number, temp: number, hum: number}[]} measurments - temperature and humidity in one list
 * @returns {[{timestamp: number, temp: number}[], {timestamp: number, hum: number}[]]} temperature and humidity split into two lists
 */
function splitMeasurementData(measurments) {
    const temp = measurments.map(({timestamp, temp}) => ({ x: timestamp*1000, y: temp}))
    const hum = measurments.map(({timestamp, hum}) => ({ x: timestamp*1000, y: hum}))
    return [temp, hum]
}

/**
 * Create temperature/humidity graphs for every client id in the database.
 * Will put them all in the "charts" element.
 * 
 */
async function setup() {
    const parent = document.getElementById("charts")
    const chartResp = await fetch("/clients")
    const clientIds = await chartResp.json()
    
    for (const clientId of clientIds) {
        const measurmentResponse = await fetch(`/clients/${clientId}`)
        const measurements = await measurmentResponse.json()

        const [temp, hum] = splitMeasurementData(measurements)
        createGraph(parent, clientId, temp, hum)
    }
}

setup()