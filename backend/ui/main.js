/**
 * Create a graph from the given temp and humidity data.
 * 
 * @param {HTMLElement} parent 
 * @param {number[]} temp 
 * @param {number[]} humidity 
 */
function createGraph(parent, temp, hum) {
    const canvas = document.createElement("canvas")
    parent.append(canvas)

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

function splitMeasurementData(measurments) {
    const temp = measurments.map(({timestamp, temp}) => ({ x: timestamp*1000, y: temp}))
    const hum = measurments.map(({timestamp, hum}) => ({ x: timestamp*1000, y: hum}))
    return [temp, hum]
}

async function setup() {
    
    const parent = document.getElementById("charts")
    const chartResp = await fetch("/clients")
    const clientIds = await chartResp.json()
    
    for (const clientId of clientIds) {
        const measurmentResponse = await fetch(`/clients/${clientId}`)
        const measurements = await measurmentResponse.json()

        const [temp, hum] = splitMeasurementData(measurements)
        createGraph(parent, temp, hum)
    }
}

setup()