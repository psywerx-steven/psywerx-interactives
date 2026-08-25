const driverList = document.querySelector("#driver-list");

function createDriverCard(driver) {
  const article = document.createElement("article");
  const layer = document.createElement("p");
  const heading = document.createElement("h3");
  const definition = document.createElement("p");

  article.className = "driver-card";
  article.dataset.driverId = driver.id;

  layer.className = "driver-layer";
  layer.textContent = driver.layer;

  heading.textContent = driver.name;

  definition.className = "driver-definition";
  definition.textContent = driver.definition;

  article.append(layer, heading, definition);
  return article;
}

async function loadDrivers() {
  try {
    const response = await fetch("../data/drivers.json");

    if (!response.ok) {
      throw new Error(`Driver data request failed with status ${response.status}.`);
    }

    const drivers = await response.json();
    driverList.replaceChildren(...drivers.map(createDriverCard));
  } catch (error) {
    console.error("Unable to load sample drivers:", error);
    const message = document.createElement("p");
    message.className = "load-error";
    message.textContent = "Sample drivers could not be loaded.";
    driverList.replaceChildren(message);
  }
}

loadDrivers();
