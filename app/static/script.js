async function fetchWeather() {
    const city = document.getElementById('city').value
    const divResultado = document.getElementById('resultado')
    const divLoading = document.getElementById('loading')

    if (!city) return alert("Please type a city")

    // UI: Mostrar 'Cargando' y ocultar resultado anterior
    divLoading.style.display = 'block'
    divResultado.style.display = 'none'

    try {
        // Hacer la petición a mi API de FastAPI, también se usa await
        const response = await fetch(`/weather?address=${city}`);

        // Verificar si hubo error
        if (!response.ok) {
            const errorData = await response.json()
            throw new Error(errorData.detail || "Error fetching the forecast")
        }

        const data = await response.json()

        // Actualizar el HTML con los datos (VisualCrossing structure)
        // Nota: VisualCrossing devuelve la temperatura actual en 'currentConditions.temp'
        document.getElementById('city_name').innerText = data.resolvedAddress
        document.getElementById('temp').innerText = data.currentConditions.temp + "°F"
        document.getElementById('desc').innerText = data.currentConditions.conditions

        // UI: Mostrar resultado
        divResultado.style.display = 'block'
    } catch (error) {
        alert("There was a problem: " + error.message)
    } finally{
        divLoading.style.display = 'none'
    }
}