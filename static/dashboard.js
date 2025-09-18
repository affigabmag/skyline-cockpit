class DashboardManager {
    constructor() {
        this.currentDate = null;
        this.availableDates = [];
        this.utilizationChart = null;
        this.init();
    }

    async init() {
        await this.loadAvailableDates();
        this.initializeChart();
        this.bindEvents();
        this.startRealTimeUpdates();
    }

    initializeChart() {
        const ctx = document.getElementById('utilizationChart');
        if (ctx) {
            this.utilizationChart = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    datasets: [{
                        data: [78, 22],
                        backgroundColor: ['#ff9500', '#555'],
                        borderWidth: 0,
                        cutout: '60%'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    circumference: 180,
                    rotation: 270,
                    plugins: {
                        legend: { display: false },
                        tooltip: { enabled: false }
                    }
                }
            });
        }
    }

    updateUtilization(percentage) {
        if (this.utilizationChart) {
            this.utilizationChart.data.datasets[0].data = [percentage, 100 - percentage];
            this.utilizationChart.update();
        }

        const text = document.querySelector('.utilization-inner');
        if (text) {
            text.textContent = `${percentage}%`;
        }
    }

    async loadAvailableDates() {
        const spinner = document.getElementById('loadingSpinner');
        if (spinner) spinner.style.display = 'inline-block';
        
        try {
            const response = await fetch('/api/available-dates');
            const data = await response.json();
            
            if (data.dates && data.dates.length > 0) {
                this.availableDates = data.dates;
                this.populateDateDropdown();
                const latestDate = data.dates[data.dates.length - 1];
                await this.loadDateData(latestDate);
            }
        } catch (error) {
            console.error('Error loading available dates:', error);
        } finally {
            if (spinner) spinner.style.display = 'none';
        }
    }

    populateDateDropdown() {
        const dropdown = document.getElementById('dateDropdown');
        if (!dropdown) return;

        dropdown.innerHTML = '';
        this.availableDates.forEach(date => {
            const option = document.createElement('option');
            option.value = date;
            option.textContent = date;
            dropdown.appendChild(option);
        });

        if (this.availableDates.length > 0) {
            dropdown.value = this.availableDates[this.availableDates.length - 1];
        }
    }

    async loadDateData(dateStr) {
        try {
            const [day, month, year] = dateStr.split('/');
            const apiDate = `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`;

            const response = await fetch(`/api/daily-report?date=${apiDate}`);
            const data = await response.json();

            this.updateDashboard(data);
            this.currentDate = dateStr;
        } catch (error) {
            console.error('Error loading date data:', error);
        }
    }

    updateDashboard(data) {
        this.updateElement('startTime', data.daily_stats?.start_time || '05:57');
        this.updateElement('endTime', data.daily_stats?.end_time || '15:54');
        this.updateElement('workingHours', data.daily_stats?.working_hours || '9:56');
        this.updateElement('utilizedHours', data.daily_stats?.utilized_hours || '7:42');

        const utilization = data.daily_stats?.utilization_percent || 78;
        this.updateUtilization(utilization);

        this.updateOperationsBreakdown(data.breakdown || {});
    }

    updateElement(id, value) {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value;
        }
    }

    updateUtilization(percentage) {
        const circle = document.getElementById('utilizationCircle');
        if (circle) {
            const degrees = (percentage / 100) * 180;
            circle.style.background = `conic-gradient(from 180deg, #ff9500 0deg ${degrees}deg, #555 ${degrees}deg 180deg)`;
        }

        const text = document.querySelector('.utilization-inner');
        if (text) {
            text.textContent = `${percentage}%`;
        }
    }

    updateOperationsBreakdown(breakdown) {
        const operations = [
            { key: 'moving_with_load', selector: '[data-operation="moving_with_load"]' },
            { key: 'moving_without_load', selector: '[data-operation="moving_without_load"]' },
            { key: 'idle_with_load', selector: '[data-operation="idle_with_load"]' },
            { key: 'idle_without_load', selector: '[data-operation="idle_without_load"]' }
        ];

        operations.forEach(op => {
            const element = document.querySelector(op.selector + ' .operation-value');
            if (element && breakdown[op.key]) {
                element.textContent = breakdown[op.key].duration || '00:00';
            }
        });
    }

    bindEvents() {
        const dateDropdown = document.getElementById('dateDropdown');
        if (dateDropdown) {
            dateDropdown.addEventListener('change', async (e) => {
                await this.loadDateData(e.target.value);
            });
        }

        // Hamburger menu functionality
        const hamburgerMenu = document.getElementById('hamburgerMenu');
        const dropdownMenu = document.getElementById('dropdownMenu');
        
        if (hamburgerMenu && dropdownMenu) {
            hamburgerMenu.addEventListener('click', (e) => {
                e.stopPropagation();
                dropdownMenu.classList.toggle('show');
            });

            // Close dropdown when clicking outside
            document.addEventListener('click', () => {
                dropdownMenu.classList.remove('show');
            });
        }
    }

    startRealTimeUpdates() {
        setInterval(() => {
            if (this.currentDate) {
                this.loadDateData(this.currentDate);
            }
        }, 30000);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new DashboardManager();
    console.log('Skyline Cockpit Dashboard initialized');
});