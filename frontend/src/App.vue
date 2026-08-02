<script setup>
import { ref } from "vue";

const savedAccessCode = sessionStorage.getItem("valery-poc-code") || "";
const accessCode = ref(savedAccessCode);
const accessConfigured = ref(Boolean(savedAccessCode));
const clientCode = ref("");
const client = ref(null);
const loading = ref(false);
const error = ref("");

function saveAccessCode() {
  error.value = "";
  if (!accessCode.value.trim()) {
    error.value = "Ingresa el código de acceso de la prueba.";
    return;
  }

  sessionStorage.setItem("valery-poc-code", accessCode.value.trim());
  accessConfigured.value = true;
}

function changeAccessCode() {
  sessionStorage.removeItem("valery-poc-code");
  accessCode.value = "";
  accessConfigured.value = false;
  client.value = null;
  error.value = "";
}

async function findClient() {
  error.value = "";
  client.value = null;

  if (!clientCode.value.trim()) {
    error.value = "Ingresa un código de cliente.";
    return;
  }

  loading.value = true;

  try {
    const response = await fetch(`/api/clients/${encodeURIComponent(clientCode.value.trim())}`, {
      headers: { "X-Poc-Code": accessCode.value.trim() }
    });
    const body = await response.json();

    if (!response.ok) {
      if (response.status === 401) changeAccessCode();
      throw new Error(body.detail || "No fue posible buscar el cliente.");
    }

    client.value = body;
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
      <h1>Consulta de clientes</h1>
      <p class="intro">
        Busca un cliente por código. La información se consulta de forma privada en Valery.
      </p>

      <form v-if="!accessConfigured" @submit.prevent="saveAccessCode">
        <label for="access-code">Código de acceso</label>
        <input
          id="access-code"
          v-model="accessCode"
          type="password"
          autocomplete="current-password"
          placeholder="Código de la prueba"
        />
        <button type="submit">Continuar</button>
      </form>

      <form v-else @submit.prevent="findClient">
        <div class="access-state">
          <span>Acceso configurado para esta sesión.</span>
          <button type="button" class="link-button" @click="changeAccessCode">
            Cambiar código de acceso
          </button>
        </div>

        <label for="client-code">Código de cliente</label>
        <input
          id="client-code"
          v-model="clientCode"
          autocomplete="off"
          placeholder="Ejemplo: 003"
        />

        <button type="submit" :disabled="loading">
          {{ loading ? "Buscando…" : "Buscar cliente" }}
        </button>
      </form>

      <p v-if="error" class="message error" role="alert">{{ error }}</p>

      <div v-if="client" class="client-card" aria-live="polite">
        <p class="client-heading">Cliente encontrado</p>
        <dl>
          <div>
            <dt>Código</dt>
            <dd>{{ client.code }}</dd>
          </div>
          <div>
            <dt>Nombre</dt>
            <dd>{{ client.name || "No registrado" }}</dd>
          </div>
          <div>
            <dt>Dirección</dt>
            <dd>{{ client.address || "No registrada" }}</dd>
          </div>
          <div>
            <dt>Teléfonos</dt>
            <dd>{{ client.phones || "No registrados" }}</dd>
          </div>
        </dl>
      </div>
    </section>
    <p class="privacy">Firebird no está publicado en Internet.</p>
  </main>
</template>
