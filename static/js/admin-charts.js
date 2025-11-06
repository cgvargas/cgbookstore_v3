/**
 * Admin Charts - Sistema de gráficos para Dashboard
 * CGBookStore v3
 */

// Configuração global do Chart.js para tema escuro
const chartDefaults = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: {
            labels: {
                color: '#e0e0e0',
                font: {
                    size: 12,
                    family: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"
                }
            }
        },
        tooltip: {
            backgroundColor: 'rgba(42, 42, 42, 0.95)',
            titleColor: '#e0e0e0',
            bodyColor: '#e0e0e0',
            borderColor: '#444',
            borderWidth: 1,
            padding: 12,
            displayColors: true,
            callbacks: {
                label: function(context) {
                    let label = context.dataset.label || '';
                    if (label) {
                        label += ': ';
                    }
                    label += context.parsed.y || context.parsed;
                    return label;
                }
            }
        }
    },
    scales: {
        x: {
            ticks: {
                color: '#999',
                font: {
                    size: 11
                }
            },
            grid: {
                color: 'rgba(255, 255, 255, 0.1)',
                drawBorder: false
            }
        },
        y: {
            ticks: {
                color: '#999',
                font: {
                    size: 11
                },
                precision: 0
            },
            grid: {
                color: 'rgba(255, 255, 255, 0.1)',
                drawBorder: false
            }
        }
    }
};

// Paleta de cores para os gráficos (tema escuro)
const chartColors = {
    primary: '#417690',
    success: '#28a745',
    warning: '#ffc107',
    danger: '#dc3545',
    info: '#17a2b8',
    secondary: '#6c757d',
    gradients: {
        blue: ['#417690', '#5a9ab8', '#73b4d0'],
        green: ['#28a745', '#34ce57', '#48e56d'],
        red: ['#dc3545', '#e74c5c', '#f16373'],
        purple: ['#6f42c1', '#8661d1', '#9d7fe0'],
        orange: ['#fd7e14', '#fd9843', '#fdb272']
    }
};

/**
 * Inicializa todos os gráficos da dashboard
 */
function initDashboardCharts() {
    console.log('Inicializando gráficos da dashboard...');

    // Aguarda DOM estar pronto
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', loadAllCharts);
    } else {
        loadAllCharts();
    }
}

/**
 * Carrega todos os gráficos
 */
function loadAllCharts() {
    console.log('Dashboard Charts: Carregando gráficos...');

    // Gráfico Livros por Categoria
    if (window.booksByCategoryData) {
        createBooksByCategoryChart();
    }
    // Gráfico Eventos por Status
    if (window.eventsByStatusData) {
        createEventsByStatusChart();
    }
    // Gráfico Origem das Capas
    if (window.coverSourceData) {
        createCoverSourceChart();
    }
    // Gráfico Crescimento de Assinaturas (Finance)
    if (window.subscriptionGrowthData) {
        createSubscriptionGrowthChart();
    }
}

/**
 * Gráfico: Livros por Categoria (Barras Horizontais)
 */
function createBooksByCategoryChart() {
    const data = window.booksByCategoryData;

    if (!data || data.labels.length === 0) {
        console.log('Sem dados para gráfico de categorias');
        return;
    }

    const config = {
        type: 'bar',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Quantidade de Livros',
                data: data.values,
                backgroundColor: chartColors.gradients.blue,
                borderColor: chartColors.primary,
                borderWidth: 1,
                borderRadius: 6,
                barThickness: 25
            }]
        },
        options: {
            ...chartDefaults,
            indexAxis: 'y', // Barras horizontais
            plugins: {
                ...chartDefaults.plugins,
                legend: {
                    display: false
                },
                tooltip: {
                    ...chartDefaults.plugins.tooltip,
                    callbacks: {
                        label: function(context) {
                            return `${context.parsed.x} livro(s)`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    ...chartDefaults.scales.x,
                    beginAtZero: true,
                    ticks: {
                        ...chartDefaults.scales.x.ticks,
                        stepSize: 1
                    }
                },
                y: {
                    ...chartDefaults.scales.y,
                    grid: {
                        display: false
                    }
                }
            }
        }
    };

    createChart('booksByCategoryChart', config);
    console.log('✅ Gráfico de Categorias carregado');
}

/**
 * Destrói um gráfico existente (útil para atualizações)
 */
function destroyChart(chartId) {
    const chartInstance = Chart.getChart(chartId);
    if (chartInstance) {
        chartInstance.destroy();
    }
}

/**
 * Cria gráfico genérico
 */
function createChart(canvasId, config) {
    destroyChart(canvasId);
    const ctx = document.getElementById(canvasId);
    if (!ctx) {
        console.error(`Canvas ${canvasId} não encontrado`);
        return null;
    }
    return new Chart(ctx, config);
}

/**
 * Gráfico: Eventos por Status (Doughnut/Rosca)
 */
function createEventsByStatusChart() {
    const data = window.eventsByStatusData;

    if (!data) {
        console.log('Sem dados para gráfico de eventos');
        return;
    }

    const total = data.upcoming + data.happening + data.finished;

    if (total === 0) {
        // Exibir mensagem quando não há eventos
        const canvas = document.getElementById('eventsByStatusChart');
        if (canvas) {
            const ctx = canvas.getContext('2d');
            ctx.font = '14px Arial';
            ctx.fillStyle = '#999';
            ctx.textAlign = 'center';
            ctx.fillText('Nenhum evento cadastrado', canvas.width / 2, canvas.height / 2);
        }
        return;
    }

    const config = {
        type: 'doughnut',
        data: {
            labels: ['Próximos', 'Acontecendo', 'Finalizados'],
            datasets: [{
                data: [data.upcoming, data.happening, data.finished],
                backgroundColor: [
                    chartColors.info,      // Azul - Próximos
                    chartColors.success,   // Verde - Acontecendo
                    chartColors.danger     // Vermelho - Finalizados
                ],
                borderColor: '#1a1a1a',
                borderWidth: 3,
                hoverOffset: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#e0e0e0',
                        font: {
                            size: 12,
                            family: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"
                        },
                        padding: 15,
                        usePointStyle: true,
                        pointStyle: 'circle'
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(42, 42, 42, 0.95)',
                    titleColor: '#e0e0e0',
                    bodyColor: '#e0e0e0',
                    borderColor: '#444',
                    borderWidth: 1,
                    padding: 12,
                    displayColors: true,
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.parsed;
                            const percentage = ((value / total) * 100).toFixed(1);
                            return `${label}: ${value} (${percentage}%)`;
                        }
                    }
                }
            },
            cutout: '65%' // Tamanho do buraco (rosca)
        }
    };

    createChart('eventsByStatusChart', config);
    console.log('✅ Gráfico de Eventos carregado');
}

/**
 * Gráfico: Origem das Capas (Pie/Pizza)
 */
function createCoverSourceChart() {
    const data = window.coverSourceData;

    if (!data) {
        console.log('Sem dados para gráfico de capas');
        return;
    }

    const total = data.from_google + data.placeholder;

    if (total === 0) {
        const canvas = document.getElementById('coverSourceChart');
        if (canvas) {
            const ctx = canvas.getContext('2d');
            ctx.font = '14px Arial';
            ctx.fillStyle = '#999';
            ctx.textAlign = 'center';
            ctx.fillText('Nenhum livro cadastrado', canvas.width / 2, canvas.height / 2);
        }
        return;
    }

    const config = {
        type: 'pie',
        data: {
            labels: ['Google Books', 'Placeholder/Sem Capa'],
            datasets: [{
                data: [data.from_google, data.placeholder],
                backgroundColor: [
                    chartColors.success,   // Verde - Google Books
                    chartColors.secondary  // Cinza - Placeholder
                ],
                borderColor: '#1a1a1a',
                borderWidth: 3,
                hoverOffset: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#e0e0e0',
                        font: {
                            size: 12,
                            family: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"
                        },
                        padding: 15,
                        usePointStyle: true,
                        pointStyle: 'circle'
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(42, 42, 42, 0.95)',
                    titleColor: '#e0e0e0',
                    bodyColor: '#e0e0e0',
                    borderColor: '#444',
                    borderWidth: 1,
                    padding: 12,
                    displayColors: true,
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.parsed;
                            const percentage = ((value / total) * 100).toFixed(1);
                            return `${label}: ${value} livros (${percentage}%)`;
                        },
                        afterLabel: function(context) {
                            if (context.dataIndex === 0) {
                                return 'Capas reais do Google';
                            } else {
                                return 'Sem capa ou placeholder';
                            }
                        }
                    }
                }
            }
        }
    };

    createChart('coverSourceChart', config);
    console.log('✅ Gráfico de Capas carregado');
}

/**
 * Gráfico: Crescimento de Assinaturas Premium (Linha)
 */
function createSubscriptionGrowthChart() {
    const data = window.subscriptionGrowthData;

    if (!data || data.labels.length === 0) {
        console.log('Sem dados para gráfico de assinaturas');
        return;
    }

    const config = {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Novas Assinaturas',
                data: data.values,
                backgroundColor: 'rgba(65, 118, 144, 0.2)',
                borderColor: chartColors.primary,
                borderWidth: 3,
                fill: true,
                tension: 0.4, // Suavização da curva
                pointRadius: 5,
                pointBackgroundColor: chartColors.primary,
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointHoverRadius: 7,
                pointHoverBackgroundColor: chartColors.primary,
                pointHoverBorderColor: '#fff',
                pointHoverBorderWidth: 3
            }]
        },
        options: {
            ...chartDefaults,
            plugins: {
                ...chartDefaults.plugins,
                legend: {
                    display: false
                },
                tooltip: {
                    ...chartDefaults.plugins.tooltip,
                    callbacks: {
                        label: function(context) {
                            return `${context.parsed.y} nova(s) assinatura(s)`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    ...chartDefaults.scales.x,
                    grid: {
                        color: 'rgba(255, 255, 255, 0.05)',
                        drawBorder: false
                    }
                },
                y: {
                    ...chartDefaults.scales.y,
                    beginAtZero: true,
                    ticks: {
                        ...chartDefaults.scales.y.ticks,
                        stepSize: 1
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.05)',
                        drawBorder: false
                    }
                }
            }
        }
    };

    createChart('subscriptionGrowthChart', config);
    console.log('✅ Gráfico de Assinaturas carregado');
}

// Exportar funções para uso global
window.DashboardCharts = {
    init: initDashboardCharts,
    destroy: destroyChart,
    create: createChart,
    colors: chartColors,
    defaults: chartDefaults
};

// Auto-inicializar
initDashboardCharts();