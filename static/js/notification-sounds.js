/**
 * =========================================================================
 * CGBookStore v3 - Sistema de Sons para Notificações
 *
 * Versão: 1.0.0
 * Data: Outubro 2025
 *
 * Funcionalidades:
 * - Sons nativos via Web Audio API (sem arquivos externos)
 * - 3 níveis de prioridade (baixa, média, alta)
 * - Toggle on/off persistente (localStorage)
 * - Integração com NotificationManager
 *
 * Uso:
 * - NotificationSounds.play(1)  // Prioridade baixa
 * - NotificationSounds.play(2)  // Prioridade média (padrão)
 * - NotificationSounds.play(3)  // Prioridade alta
 * - NotificationSounds.toggle() // Ativar/desativar
 * =========================================================================
 */

const NotificationSounds = (() => {
    /**
     * Configurações do sistema de sons
     */
    const config = {
        enabled: true,           // Som ativo por padrão
        volume: 0.3,            // Volume (0.0 a 1.0)
        duration: 0.15,         // Duração do som em segundos
        storageKey: 'notificationSoundsEnabled'
    };

    /**
     * Frequências para cada nível de prioridade
     * Baseadas em notas musicais para sons agradáveis
     */
    const frequencies = {
        1: { note: 523.25, label: 'Baixa' },    // Dó (C5) - Som suave
        2: { note: 659.25, label: 'Média' },    // Mi (E5) - Som moderado
        3: { note: 783.99, label: 'Alta' }      // Sol (G5) - Som urgente
    };

    /**
     * Contexto de áudio (criado sob demanda)
     */
    let audioContext = null;

    /**
     * Inicializa o AudioContext
     * Nota: AudioContext deve ser criado após interação do usuário (política do navegador)
     */
    function initAudioContext() {
        if (!audioContext) {
            try {
                audioContext = new (window.AudioContext || window.webkitAudioContext)();
                console.log('🔊 AudioContext inicializado');
            } catch (error) {
                console.error('❌ Erro ao criar AudioContext:', error);
                return false;
            }
        }

        // Retomar contexto se estiver suspenso
        if (audioContext.state === 'suspended') {
            audioContext.resume();
        }

        return true;
    }

    /**
     * Carrega preferências do localStorage
     */
    function loadPreferences() {
        try {
            const saved = localStorage.getItem(config.storageKey);
            if (saved !== null) {
                config.enabled = JSON.parse(saved);
                console.log(`🔊 Sons ${config.enabled ? 'ativados' : 'desativados'} (localStorage)`);
            }
        } catch (error) {
            console.error('❌ Erro ao carregar preferências de som:', error);
        }
    }

    /**
     * Salva preferências no localStorage
     */
    function savePreferences() {
        try {
            localStorage.setItem(config.storageKey, JSON.stringify(config.enabled));
            console.log(`💾 Preferência de som salva: ${config.enabled}`);
        } catch (error) {
            console.error('❌ Erro ao salvar preferências de som:', error);
        }
    }

    /**
     * Toca um som com a prioridade especificada
     *
     * @param {number} priority - Nível de prioridade (1=baixa, 2=média, 3=alta)
     * @returns {boolean} - true se o som foi tocado, false caso contrário
     */
    function play(priority = 2) {
        // Validar entrada
        if (!frequencies[priority]) {
            console.warn(`⚠️ Prioridade inválida: ${priority}. Usando prioridade 2 (média)`);
            priority = 2;
        }

        // Verificar se som está ativado
        if (!config.enabled) {
            console.log('🔇 Som desativado pelo usuário');
            return false;
        }

        // Inicializar AudioContext
        if (!initAudioContext()) {
            console.error('❌ AudioContext não disponível');
            return false;
        }

        try {
            playBeep(frequencies[priority].note, priority);
            console.log(`🔊 Som tocado: Prioridade ${priority} (${frequencies[priority].label}) - ${frequencies[priority].note}Hz`);
            return true;
        } catch (error) {
            console.error('❌ Erro ao tocar som:', error);
            return false;
        }
    }

    /**
     * Toca um beep com a frequência especificada
     *
     * @param {number} frequency - Frequência em Hz
     * @param {number} priority - Prioridade (afeta o envelope do som)
     */
    function playBeep(frequency, priority) {
        const currentTime = audioContext.currentTime;

        // Criar oscilador (gerador de som)
        const oscillator = audioContext.createOscillator();
        oscillator.type = 'sine'; // Onda senoidal (som mais suave)
        oscillator.frequency.setValueAtTime(frequency, currentTime);

        // Criar ganho (controle de volume)
        const gainNode = audioContext.createGain();

        // Envelope ADSR simplificado (Attack, Decay, Sustain, Release)
        const attack = 0.01;  // 10ms de ataque
        const decay = 0.05;   // 50ms de decaimento
        const sustain = priority === 3 ? 0.7 : 0.5; // Sustain maior para prioridade alta
        const release = 0.09; // 90ms de release

        // Configurar envelope de volume
        gainNode.gain.setValueAtTime(0, currentTime);
        gainNode.gain.linearRampToValueAtTime(config.volume, currentTime + attack);
        gainNode.gain.linearRampToValueAtTime(config.volume * sustain, currentTime + attack + decay);
        gainNode.gain.setValueAtTime(config.volume * sustain, currentTime + config.duration - release);
        gainNode.gain.linearRampToValueAtTime(0, currentTime + config.duration);

        // Conectar: Oscillator → Gain → Destination (alto-falante)
        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);

        // Tocar e parar automaticamente
        oscillator.start(currentTime);
        oscillator.stop(currentTime + config.duration);

        // Limpeza após tocar
        oscillator.onended = () => {
            oscillator.disconnect();
            gainNode.disconnect();
        };
    }

    /**
     * Alterna o estado do som (ativado/desativado)
     *
     * @returns {boolean} - Novo estado (true=ativado, false=desativado)
     */
    function toggle() {
        config.enabled = !config.enabled;
        savePreferences();

        // Tocar som de confirmação se foi ativado
        if (config.enabled) {
            // Pequeno delay para garantir que o AudioContext esteja pronto
            setTimeout(() => play(1), 100);
        }

        console.log(`🔊 Sons ${config.enabled ? 'ativados' : 'desativados'}`);
        return config.enabled;
    }

    /**
     * Verifica se o som está ativado
     *
     * @returns {boolean}
     */
    function isEnabled() {
        return config.enabled;
    }

    /**
     * Ativa o som
     */
    function enable() {
        if (!config.enabled) {
            toggle();
        }
    }

    /**
     * Desativa o som
     */
    function disable() {
        if (config.enabled) {
            toggle();
        }
    }

    /**
     * Obtém o volume atual
     *
     * @returns {number} Volume (0.0 a 1.0)
     */
    function getVolume() {
        return config.volume;
    }

    /**
     * Define o volume
     *
     * @param {number} value - Novo volume (0.0 a 1.0)
     */
    function setVolume(value) {
        if (value >= 0 && value <= 1) {
            config.volume = value;
            console.log(`🔊 Volume ajustado para: ${Math.round(value * 100)}%`);
        } else {
            console.warn('⚠️ Volume deve estar entre 0 e 1');
        }
    }

    /**
     * Testa todos os sons
     */
    function testAllSounds() {
        console.log('🎵 Testando todos os sons...');

        play(1); // Baixa

        setTimeout(() => {
            play(2); // Média
        }, 500);

        setTimeout(() => {
            play(3); // Alta
        }, 1000);
    }

    // Inicialização
    loadPreferences();

    // Interface pública
    return {
        play,
        toggle,
        isEnabled,
        enable,
        disable,
        getVolume,
        setVolume,
        testAllSounds
    };
})();

// Disponibilizar globalmente
window.NotificationSounds = NotificationSounds;

// Log de inicialização
console.log('🔊 NotificationSounds v1.0.0 inicializado');
console.log(`   Status: ${NotificationSounds.isEnabled() ? 'Ativado ✅' : 'Desativado 🔇'}`);
console.log('   Comandos disponíveis no console:');
console.log('   - NotificationSounds.play(1)      // Som de prioridade baixa');
console.log('   - NotificationSounds.play(2)      // Som de prioridade média');
console.log('   - NotificationSounds.play(3)      // Som de prioridade alta');
console.log('   - NotificationSounds.toggle()     // Ativar/Desativar');
console.log('   - NotificationSounds.testAllSounds() // Testar todos os sons');