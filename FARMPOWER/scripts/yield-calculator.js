// Crop yield calculator functionality
const yieldCalculator = {
    // Initialize the calculator
    async init(map, draw) {
        this.map = map;
        this.draw = draw;
        await this.loadCropTypes();
        this.setupEventListeners();
    },

    // Load available crop types from API
    async loadCropTypes() {
        try {
            const response = await fetch('/api/crops');
            const crops = await response.json();
            this.populateCropSelect(crops);
        } catch (error) {
            console.error('Error loading crop types:', error);
        }
    },

    // Populate crop type select dropdown
    populateCropSelect(crops) {
        const select = document.getElementById('cropType');
        if (!select) return;

        select.innerHTML = Object.keys(crops).map(crop => 
            `<option value="${crop}">${crop.charAt(0).toUpperCase() + crop.slice(1)}</option>`
        ).join('');
    },

    // Setup event listeners
    setupEventListeners() {
        // Listen for new drawings
        this.draw.on('draw.create', (e) => this.handleNewField(e.features[0]));
        
        // Listen for field selection
        this.map.on('click', 'fields-layer', (e) => this.handleFieldClick(e));
        
        // Form submission
        const form = document.getElementById('fieldForm');
        if (form) {
            form.addEventListener('submit', (e) => this.handleFormSubmit(e));
        }
    },

    // Handle new field drawing
    async handleNewField(feature) {
        const area = turf.area(feature.geometry);
        document.querySelector('[name="area"]').value = (area / 4046.86).toFixed(2); // Convert to acres
        document.querySelector('[name="boundaries"]').value = JSON.stringify(feature.geometry);
        showFieldForm();
    },

    // Handle field selection
    handleFieldClick(e) {
        if (!e.features.length) return;

        const feature = e.features[0];
        this.showFieldStats(feature.properties);
    },

    // Show field statistics
    showFieldStats(properties) {
        const statsDiv = document.getElementById('field-stats');
        const content = document.getElementById('stats-content');
        
        if (!statsDiv || !content) return;

        content.innerHTML = `
            <div class="space-y-2">
                <p><strong>Name:</strong> ${properties.name}</p>
                <p><strong>Crop:</strong> ${properties.cropType}</p>
                <p><strong>Area:</strong> ${properties.area} acres</p>
                <p><strong>Expected Yield:</strong> ${properties.expectedYield} tons</p>
                <p><strong>Yield per Acre:</strong> ${properties.yieldPerAcre} tons</p>
            </div>
        `;

        statsDiv.classList.remove('hidden');
    },

    // Handle form submission
    async handleFormSubmit(e) {
        e.preventDefault();
        
        const formData = new FormData(e.target);
        const fieldData = {
            name: formData.get('name'),
            geometry: JSON.parse(formData.get('boundaries')),
            crop_type: formData.get('cropType'),
            soil_type: formData.get('soilType') || 'loam',
            irrigation: formData.get('irrigation') === 'on'
        };

        try {
            const response = await fetch('/api/calculate-yield', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(fieldData)
            });

            if (!response.ok) throw new Error('Failed to calculate yield');

            const result = await response.json();
            this.addFieldToMap(fieldData, result);
            hideFieldForm();
        } catch (error) {
            console.error('Error calculating yield:', error);
            alert('Error calculating yield. Please try again.');
        }
    },

    // Add field to map
    addFieldToMap(field, yieldData) {
        const feature = {
            type: 'Feature',
            geometry: field.geometry,
            properties: {
                name: field.name,
                cropType: field.crop_type,
                area: yieldData.area_hectares * 2.47105, // Convert to acres
                expectedYield: yieldData.expected_yield_tons,
                yieldPerAcre: (yieldData.yield_per_hectare * 0.404686).toFixed(2), // Convert to tons per acre
                soilType: field.soil_type,
                irrigation: field.irrigation
            }
        };

        // Add to map source
        const source = this.map.getSource('fields');
        const features = source.serialize().data.features || [];
        features.push(feature);
        
        source.setData({
            type: 'FeatureCollection',
            features: features
        });
    }
};

// Export for use in main map script
window.yieldCalculator = yieldCalculator;