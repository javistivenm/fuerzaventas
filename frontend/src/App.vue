<script setup>
import { computed, ref } from "vue";

const accessCode = ref(sessionStorage.getItem("valery-poc-code") || "");
const loading = ref(false);
const result = ref(null);
const error = ref("");

const checkedAt = computed(() => {
  if (!result.value?.checked_at) return "";
  return new Intl.DateTimeFormat("es", {
    dateStyle: "medium",
    timeStyle: "medium"
  }).format(new Date(result.value.checked_at));
});

async function testConnection() {
  error.value = "";
  result.value = null;

  if (!accessCode.value.trim()) {
    error.value = "Ingresa el código de acceso de la prueba.";
    return;
  }

  sessionStorage.setItem("valery-poc-code", accessCode.value.trim());
  loading.value = true;

  try {
    const response = await fetch("/api/poc/status", {
      headers: { "X-Poc-Code": accessCode.value.trim() }
    });
    const body = await response.json();

    if (!response.ok) {
      throw new Error(body.detail || "No fue posible ejecutar la prueba.");
    }

    result.value = body;
  } catch (requestError) {
    error.value = requestError.message || "Error inesperado.";
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <main class="shell">
    <section class="card">
      <div class="eyebrow">PRUEBA DE CONCEPTO</div>
      <h1>Conexión con Valery</h1>
      <p class="intro">
        Comprueba el enlace privado desde este celular hasta Firebird 2.5,
        pasando por el VPS y Tailscale.
      </p>

      <label for="access-code">Código de acceso</label>
      <input
        id="access-code"
        v-model="accessCode"
        type="password"
        autocomplete="current-password"
        placeholder="Código de la prueba"
        @keyup.enter="testConnection"
      />

      <button :disabled="loading" @click="testConnection">
        {{ loading ? "Comprobando…" : "Probar conexión" }}
      </button>

      <p v-if="error" class="message error" role="alert">{{ error }}</p>

      <div v-if="result" class="results" aria-live="polite">
        <div class="status-row">
          <span :class="['dot', result.vps.ok ? 'ok' : 'bad']"></span>
          <div>
            <strong>Backend del VPS</strong>
            <small>{{ result.vps.message }}</small>
          </div>
        </div>
        <div class="status-row">
          <span :class="['dot', result.bridge.ok ? 'ok' : 'bad']"></span>
          <div>
            <strong>Puente Windows</strong>
            <small>{{ result.bridge.message }}</small>
          </div>
        </div>
        <div class="status-row">
          <span :class="['dot', result.firebird.ok ? 'ok' : 'bad']"></span>
          <div>
            <strong>Valery / Firebird 2.5</strong>
            <small>{{ result.firebird.message }}</small>
          </div>
        </div>

        <div v-if="result.firebird.server_time" class="server-time">
          Hora reportada por Firebird
          <strong>{{ result.firebird.server_time }}</strong>
        </div>
        <p class="checked">Última prueba: {{ checkedAt }}</p>
      </div>
    </section>
    <p class="privacy">Firebird no está publicado en Internet.</p>
  </main>
</template>

