/**
 * Get the name for the given id if such a name has been stored,
 * otherwise return the id.
 * 
 * @param {string} id 
 * @returns 
 */
function getClientName(id) {
    const name = localStorage.getItem(id) || id
    return name.replaceAll(/["<>]/g, "")
}

/**
 * Set an alternative name for the given client id. It will strip "<> from the string.
 * 
 * If the name is null or just whitespace any name will be removed instead.
 * 
 * @param {string} id 
 * @param {string} name 
 */
function setClientName(id, name) {
    if (name != null && name.trim().length > 0) {
        const safeName = name.replaceAll(/["<>]/g, "")
        if (safeName.trim().length > 0) {
            localStorage.setItem(id, safeName)
            return
        }
    }
    
    localStorage.removeItem(id)
}

/**
 * Create a html elements from the given HTML fragment string.
 * 
 * @param {string} html
 * @returns {HTMLCollection}
 */
function createElementsFromHTML(html) {
    var div = document.createElement('div');
    div.innerHTML = html;
    return div.children;
}

/**
 * Enable editing of the given parents name.
 * 
 * @param {MouseEvent} event 
 * @param {HTMLElement} parent
 */
function editName(event, parent) {
    const clientId = parent.dataset.clientId
    const name = getClientName(clientId)
    const target = parent.querySelector(".editable-heading")
    const content = Array.from(target.children)

    const edit = createElementsFromHTML(`
        <form>
            <input type="text" value="${name}">
            <button class="btn-submit" type="submit">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-check" viewBox="0 0 16 16">
                    <path d="M10.97 4.97a.75.75 0 0 1 1.07 1.05l-3.99 4.99a.75.75 0 0 1-1.08.02L4.324 8.384a.75.75 0 1 1 1.06-1.06l2.094 2.093 3.473-4.425a.267.267 0 0 1 .02-.022z"/>
                </svg>
            </button>
            <button class="btn-cancel">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-x" viewBox="0 0 16 16">
                    <path d="M4.646 4.646a.5.5 0 0 1 .708 0L8 7.293l2.646-2.647a.5.5 0 0 1 .708.708L8.707 8l2.647 2.646a.5.5 0 0 1-.708.708L8 8.707l-2.646 2.647a.5.5 0 0 1-.708-.708L7.293 8 4.646 5.354a.5.5 0 0 1 0-.708z"/>
                </svg>
            </button>
        </form>
    `)

    const form = edit[0]
    const input = form.querySelector("input")
    const btnCancel = form.querySelector(".btn-cancel")

    form.addEventListener("submit", e => {
        e.preventDefault()

        if (input.value.trim().length > 0) {
            setClientName(clientId, input.value.trim())
            for (const elem of content) {
                if (elem.tagName === 'H2') {
                    elem.innerText = getClientName(clientId)
                }
            }
            target.innerHTML = ""
            target.append(...content)    
        }
    })

    btnCancel.addEventListener("click", e => {
        target.innerHTML = ""
        target.append(...content)
    })

    target.innerHTML = ""
    target.append(...edit)

    input.setSelectionRange(0, input.value.length)
    input.focus()
}

/**
 * Create a graph from the given temp and humidity data.
 * 
 * @param {HTMLElement} parent 
 * @param {string} id
 * @param {number[]} temp 
 * @param {number[]} humidity 
 */
function createGraph(parent, id, temp, hum) {
    const name = getClientName(id)
    const elems = createElementsFromHTML(`
        <section data-client-id="${id}">
            <div class="editable-heading">
                <h2>${name}</h2>
                <button>
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-pencil" viewBox="0 0 16 16">
                        <path d="M12.146.146a.5.5 0 0 1 .708 0l3 3a.5.5 0 0 1 0 .708l-10 10a.5.5 0 0 1-.168.11l-5 2a.5.5 0 0 1-.65-.65l2-5a.5.5 0 0 1 .11-.168l10-10zM11.207 2.5 13.5 4.793 14.793 3.5 12.5 1.207 11.207 2.5zm1.586 3L10.5 3.207 4 9.707V10h.5a.5.5 0 0 1 .5.5v.5h.5a.5.5 0 0 1 .5.5v.5h.293l6.5-6.5zm-9.761 5.175-.106.106-1.528 3.821 3.821-1.528.106-.106A.5.5 0 0 1 5 12.5V12h-.5a.5.5 0 0 1-.5-.5V11h-.5a.5.5 0 0 1-.468-.325z"/>
                    </svg>
                </button>
            </div>
            <canvas></canvas>
        </section>
    `)

    const section = elems[0];
    const edit = section.querySelector("button")
    const canvas = section.querySelector("canvas")

    edit.addEventListener("click", e => editName(e, section))

    parent.append(...elems)

    const pointStyle = temp.length < 100 && hum.length < 100 ? 'circle' : false

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
                    pointStyle,
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
                            hour: "MM-dd HH:mm",
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