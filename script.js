// Reset Button
function resetForm() {
    document.querySelectorAll("input, select").forEach(el => {
        if (el.type === "radio") {
            el.checked = false;
        } else {
            el.value = "";
        }
    });

    const modelSelect = document.getElementById("model");
    modelSelect.innerHTML = '<option value="">Select Model of your Car</option>';

    document.getElementById("owner1").checked = true;

    const result = document.getElementById("result");
    result.className = "initial-message";
    result.textContent = "Please fill the form to get the estimated value of your car.";
}

// Filtering Models by Brand Names
const brandModelMap = {
    'Maruti': ['Wagon R 1.0', 'Alto 800', 'Ertiga', 'New Wagon-R', 'S PRESSO', 'Alto K10', 'Baleno', 'Swift', 'Swift Dzire', 'Ciaz', 'Celerio', 'Grand Vitara', 'BREZZA', 'Alto', 'Eeco', 'Celerio X', 'Vitara Brezza', 'FRONX', 'S Cross', 'Ritz', 'Dzire', 'IGNIS', 'XL6'],
    'Tata': ['Tiago', 'Zest', 'NEXON', 'Harrier', 'PUNCH', 'TIGOR', 'ALTROZ', 'TIAGO NRG', 'Safari', 'Curvv', 'Bolt', 'Hexa'],
    'Nissan': ['MAGNITE', 'Micra Active', 'Micra', 'Kicks', 'Terrano'],
    'Renault': ['Kwid', 'TRIBER', 'Kiger', 'Duster', 'Captur'],
    'Hyundai': ['Xcent', 'Eon', 'VENUE', 'Grand i10', 'i10', 'Verna', 'NEW I20', 'AURA', 'GRAND I10 NIOS', 'NEW SANTRO', 'Creta', 'Elite i20', 'NEW I20 N LINE', 'i20 Active', 'i20', 'EXTER', 'Tucson'],
    'Honda': ['Amaze', 'City', 'WR-V', 'Brio', 'Jazz', 'BR-V', 'ELEVATE', 'Mobilio'],
    'KIA': ['SONET', 'SELTOS', 'CARENS'],
    'MG': ['ASTOR', 'HECTOR', 'HECTOR PLUS'],
    'Ford': ['FREESTYLE', 'Figo Aspire', 'Ecosport', 'Figo', 'New Figo'],
    'Skoda': ['Rapid', 'KUSHAQ', 'SLAVIA', 'Superb', 'Fabia', 'Octavia'],
    'Volkswagen': ['Polo', 'VIRTUS', 'TAIGUN', 'TIGUAN', 'Vento', 'Ameo'],
    'Mahindra': ['Thar', 'Bolero', 'XUV300', 'XUV500', 'TUV300', 'SCORPIO-N', 'Kuv100', 'KUV 100 NXT', 'BOLERO NEO', 'XUV700', 'Scorpio'],
    'Toyota': ['URBAN CRUISER', 'Glanza', 'YARIS', 'Etios', 'Innova', 'Corolla Altis'],
    'Jeep': ['Compass'],
    'Datsun': ['Redi Go', 'Go'],
    'Audi': ['Q3', 'A6', 'A4', 'A3'],
    'BMW': ['1 Series', 'X1', '3 Series', '5 Series'],
    'Mercedes': ['Benz C Class', 'Benz GLA Class', 'Benz CLA Class'],
};

document.getElementById('brand').addEventListener('change', function () {
    const selectedBrand = this.value;
    const modelSelect = document.getElementById('model');

    modelSelect.innerHTML = '<option value="">Select Model of your Car</option>';

    if (selectedBrand && brandModelMap[selectedBrand]) {
        brandModelMap[selectedBrand].forEach(model => {
            const option = document.createElement('option');
            option.value = model;
            option.textContent = model;
            modelSelect.appendChild(option);
        });
    }
});

// Prediction Function
async function predict() {
    const resultElement = document.getElementById("result");
    resultElement.className = "";

    const brand = document.getElementById("brand").value;
    const model = document.getElementById("model").value;
    const km_driven = parseInt(document.getElementById("km_driven").value);
    const engine_capacity = parseInt(document.getElementById("engine_capacity").value);
    const fuel_type = document.getElementById("fuel_type").value;
    const transmission = document.getElementById("transmission").value;
    const year = parseInt(document.getElementById("year").value);
    const ownerRadios = document.getElementsByName("owner_type");
    let owner = "";
    for (const radio of ownerRadios) {
        if (radio.checked) {
            owner = radio.value;
            break;
        }
    }

    // Validation Check for Inputs
    if (!brand || !model || !km_driven || !engine_capacity || !fuel_type || !transmission || !year || !owner) {
        document.getElementById('result').textContent = "Please fill all the details.";
        return;
    }

    // Showing Loading Indicator while Prediction
    resultElement.className = "loading";
    resultElement.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Estimating the value of your car.....`;

    // Structure of Input
    const data = {
        brand: brand,
        model: model,
        km_driven: km_driven,
        engine_capacity: engine_capacity,
        fuel_type: fuel_type,
        transmission: transmission,
        year: year,
        owner: owner,
    };

    // API Request for Prediction
    try {
        const fetchPromise = fetch("http://127.0.0.1:8000/predict", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data),
        }).then(async res => {
            if (res.status === 429) {
                throw new Error("RateLimitExceeded");
            }
            return res.json();
        });

        const delayPromise = new Promise(resolve => setTimeout(resolve, 1500));
        const [result] = await Promise.all([fetchPromise, delayPromise]);
        
        resultElement.className = "result-success";
        resultElement.innerText = "Estimated value of your car is from " + result.output;
    } catch (error) {
        resultElement.className = "result-error";
        if (error.message === "RateLimitExceeded") {
                resultElement.innerText = "You're making requests too fast. Please wait a minute and try again.";
            } else {
                resultElement.innerText = "Something went wrong. Please try again.";
            }
    }
};