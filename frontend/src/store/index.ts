import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface User {
  id: string;
  nombre: string;
  email: string;
  rol_id: number;
  especialidad_id?: number;
}

interface Permisos {
  dashboard?: boolean;
  simulacros?: boolean;
  temas_debiles?: boolean;
  flashcards?: boolean;
  comunidad?: boolean;
}

interface AppState {
  user: User | null;
  isAuthenticated: boolean;
  permisos: Permisos;
  sidebarOpen: boolean;
  setUser: (user: User | null) => void;
  setAuthenticated: (value: boolean) => void;
  setPermisos: (permisos: Permisos) => void;
  toggleSidebar: () => void;
  logout: () => void;
}

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      user: null,
      isAuthenticated: false,
      permisos: {},
      sidebarOpen: true,
      setUser: (user) => set({ user, isAuthenticated: !!user }),
      setAuthenticated: (isAuthenticated) => set({ isAuthenticated }),
      setPermisos: (permisos) => set({ permisos }),
      toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
      logout: () => set({ user: null, isAuthenticated: false, permisos: {} }),
    }),
    {
      name: 'akademus-storage',
      partialize: (state) => ({ user: state.user, isAuthenticated: state.isAuthenticated }),
    }
  )
);

interface SimulacroState {
  simulacroId: number | null;
  preguntaActual: number;
  totalPreguntas: number;
  respuestas: Map<number, number>;
  tiempoRestante: number;
  setSimulacro: (id: number, total: number) => void;
  setPregunta: (orden: number) => void;
  agregarRespuesta: (preguntaId: number, opcionId: number) => void;
  setTiempo: (segundos: number) => void;
  reset: () => void;
}

export const useSimulacroStore = create<SimulacroState>()((set) => ({
  simulacroId: null,
  preguntaActual: 1,
  totalPreguntas: 0,
  respuestas: new Map(),
  tiempoRestante: 0,
  setSimulacro: (id, total) => set({ simulacroId: id, totalPreguntas: total, preguntaActual: 1, respuestas: new Map() }),
  setPregunta: (orden) => set({ preguntaActual: orden }),
  agregarRespuesta: (preguntaId, opcionId) => set((state) => {
    const newRespuestas = new Map(state.respuestas);
    newRespuestas.set(preguntaId, opcionId);
    return { respuestas: newRespuestas };
  }),
  setTiempo: (segundos) => set({ tiempoRestante: segundos }),
  reset: () => set({ simulacroId: null, preguntaActual: 1, totalPreguntas: 0, respuestas: new Map(), tiempoRestante: 0 }),
}));

interface FlashcardState {
  flashcardActual: number;
  total: number;
  mostrandoDorso: boolean;
  setFlashcard: (index: number, total?: number) => void;
  toggleDorso: () => void;
  siguiente: () => void;
  reset: () => void;
}

export const useFlashcardStore = create<FlashcardState>()((set) => ({
  flashcardActual: 0,
  total: 0,
  mostrandoDorso: false,
  setFlashcard: (index, total) => set({ flashcardActual: index, total: total, mostrandoDorso: false }),
  toggleDorso: () => set((state) => ({ mostrandoDorso: !state.mostrandoDorso })),
  siguiente: () => set((state) => ({ flashcardActual: state.flashcardActual + 1, mostrandoDorso: false })),
  reset: () => set({ flashcardActual: 0, total: 0, mostrandoDorso: false }),
}));
