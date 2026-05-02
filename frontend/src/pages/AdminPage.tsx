import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card } from '../components/common/Card';
import { BookOpen, Users, BarChart3, Settings, Plus, Trash2, Edit, X, FolderTree, GraduationCap, ListChecks, Layers, BookMarked, GraduationCapIcon, Trophy, Search, CheckCircle, XCircle, Clock } from 'lucide-react';
import { usersAPI, adminAPI } from '../services/api';
import api from '../services/api';

interface Bloque {
  id?: number;
  codigo: string;
  nombre: string;
  descripcion: string;
  orden: number;
  activo: boolean;
}

interface Area {
  id?: number;
  bloque_id: number;
  bloque_nombre?: string;
  codigo: string;
  nombre: string;
  descripcion: string;
  orden: number;
  activo: boolean;
}

interface Asignatura {
  id?: number;
  area_id: number;
  area_nombre?: string;
  nombre: string;
  descripcion: string;
  orden: number;
  activo: boolean;
}

interface GrupoAcad {
  id?: number;
  codigo: string;
  nombre: string;
  descripcion: string;
  orden: number;
  activo: boolean;
}

interface Especialidad {
  id?: number;
  nombre: string;
  grupo_academico_id: number;
  grupo_nombre?: string;
  codigo: string;
  puntaje_minimo: number;
  orden: number;
}

interface Opcion {
  id?: number;
  pregunta_id: number;
  texto: string;
  es_correcta: boolean;
  activa: boolean;
}

interface ConfigPuntaje {
  id?: number;
  grupo_academico_id: number;
  grupo_nombre?: string;
  asignatura_id: number;
  asignatura_nombre?: string;
  numero_preguntas: number;
  puntaje_pregunta: number;
  activo: boolean;
}

interface Curso {
  id?: number;
  nombre: string;
  descripcion: string;
  orden: number;
  imagen_url: string;
  activo: boolean;
}

interface Tema {
  id?: number;
  nombre: string;
  curso_id: number;
  curso_nombre?: string;
  dificultad_base: number;
  imagen_url: string;
  activo: boolean;
}

interface Pregunta {
  id?: number;
  tema_id: number;
  asignatura_id?: number;
  enunciado: string;
  explicacion: string;
  dificultad: number;
  tipo_id: number;
  tipo_nombre?: string;
  tema_nombre?: string;
  asignatura_nombre?: string;
  imagen_url?: string;
  activa: boolean;
  estado?: string;
  motivo_rechazo?: string;
  usuario_id?: number;
  usuario_email?: string;
}

export default function AdminPage() {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('dashboard');
  const [stats, setStats] = useState<any>(null);
  const [usuarios, setUsuarios] = useState<any[]>([]);
  const [bloques, setBloques] = useState<Bloque[]>([]);
  const [areas, setAreas] = useState<Area[]>([]);
  const [asignaturas, setAsignaturas] = useState<Asignatura[]>([]);
  const [gruposAcad, setGruposAcad] = useState<GrupoAcad[]>([]);
  const [especialidades, setEspecialidades] = useState<Especialidad[]>([]);
  const [configPuntaje, setConfigPuntaje] = useState<ConfigPuntaje[]>([]);
  const [cursos, setCursos] = useState<Curso[]>([]);
  const [temas, setTemas] = useState<Tema[]>([]);
  const [preguntas, setPreguntas] = useState<Pregunta[]>([]);
  const [opciones, setOpciones] = useState<Opcion[]>([]);
  const [selectedPregunta, setSelectedPregunta] = useState<Pregunta | null>(null);
  const [showOpcionesModal, setShowOpcionesModal] = useState(false);
  const [loading, setLoading] = useState(true);
  
  const [showModal, setShowModal] = useState(false);
  const [modalMode, setModalMode] = useState<'create' | 'edit'>('create');
  const [editingItem, setEditingItem] = useState<any>(null);
  const [tiposPregunta, setTiposPregunta] = useState<any[]>([]);
  const [filtroAsignatura, setFiltroAsignatura] = useState<string>('todas');
  const [busqueda, setBusqueda] = useState('');
  const [filtroGrupo, setFiltroGrupo] = useState<string>('todos');
  const [filtroEstado, setFiltroEstado] = useState<string>('');
  const [permisosEditando, setPermisosEditando] = useState<any>({});
  const [publicidad, setPublicidad] = useState<any[]>([]);
  const [newPubUrl, setNewPubUrl] = useState('');
  const [newPubLink, setNewPubLink] = useState('');
  const [newPubDesc, setNewPubDesc] = useState('');

  const tabs = [
    { id: 'dashboard', label: 'Dashboard', icon: BarChart3 },
    { id: 'usuarios', label: 'Usuarios', icon: Users },
    { id: 'permisos', label: 'Permisos', icon: Settings },
    { id: 'bloques', label: 'Bloques', icon: FolderTree },
    { id: 'areas', label: 'Áreas', icon: FolderTree },
    { id: 'asignaturas', label: 'Asignaturas', icon: BookMarked },
    { id: 'grupos-acad', label: 'Grupos', icon: GraduationCap },
    { id: 'especialidades', label: 'Especialidades', icon: Trophy },
    { id: 'config-puntaje', label: 'Config Puntaje', icon: Trophy },
    { id: 'cursos', label: 'Cursos', icon: Settings },
    { id: 'temas', label: 'Temas', icon: Settings },
    { id: 'preguntas', label: 'Preguntas', icon: ListChecks },
    { id: 'novedades', label: 'Novedades', icon: Clock },
    { id: 'publicidad', label: 'Publicidad', icon: Settings },
  ];

  useEffect(() => {
    loadData();
  }, [activeTab]);

  const loadData = async () => {
    setLoading(true);
    try {
      const userRes = await usersAPI.me();
      // rol_id 1 = admin pode acceder, rol_id 2 = usuario NO (redirigir)
      if (userRes.data.rol_id !== 1) {
        navigate('/dashboard');
        return;
      }

      if (activeTab === 'dashboard') {
        const res = await api.get('/admin/estadisticas');
        setStats(res.data);
      } else if (activeTab === 'usuarios') {
        const res = await api.get('/admin/usuarios');
        setUsuarios(res.data);
      } else if (activeTab === 'bloques') {
        const res = await api.get('/admin/bloques');
        setBloques(res.data);
      } else if (activeTab === 'areas') {
        const res = await api.get('/admin/areas');
        setAreas(res.data);
        const bloquesRes = await api.get('/admin/bloques');
        setBloques(bloquesRes.data);
      } else if (activeTab === 'asignaturas') {
        const res = await api.get('/admin/asignaturas');
        setAsignaturas(res.data);
        const areasRes = await api.get('/admin/areas');
        setAreas(areasRes.data);
      } else if (activeTab === 'grupos-acad') {
        const res = await api.get('/admin/grupos-academicos');
        setGruposAcad(res.data);
      } else if (activeTab === 'especialidades') {
        const res = await api.get('/admin/especialidades');
        setEspecialidades(res.data);
        const gruposRes = await api.get('/admin/grupos-academicos');
        setGruposAcad(gruposRes.data);
      } else if (activeTab === 'config-puntaje') {
        const res = await api.get('/admin/config-puntaje');
        setConfigPuntaje(res.data);
        const gruposRes = await api.get('/admin/grupos-academicos');
        setGruposAcad(gruposRes.data);
        const asigRes = await api.get('/admin/asignaturas');
        setAsignaturas(asigRes.data);
      } else if (activeTab === 'cursos') {
        const res = await api.get('/admin/cursos');
        setCursos(res.data);
      } else if (activeTab === 'temas') {
        const res = await api.get('/admin/temas');
        setTemas(res.data);
        const cursosRes = await api.get('/admin/cursos');
        setCursos(cursosRes.data);
      } else if (activeTab === 'preguntas') {
        const res = await api.get('/admin/preguntas');
        setPreguntas(res.data);
        const asigRes = await api.get('/admin/asignaturas');
        setAsignaturas(asigRes.data);
      } else if (activeTab === 'novedades') {
        const res = await api.get('/admin/preguntas?estado=pendiente');
        setPreguntas(res.data);
        const asigRes = await api.get('/admin/asignaturas');
        setAsignaturas(asigRes.data);
      } else if (activeTab === 'publicidad') {
        const res = await api.get('/admin/publicidad');
        setPublicidad(res.data);
      } else if (activeTab === 'permisos') {
        const res = await adminAPI.getUsuariosPermisos();
        const data = res.data;
        if (Array.isArray(data)) {
          setUsuarios(data);
        } else {
          console.error('Error loading permisos:', data);
          setUsuarios([]);
        }
      }
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  };

  const loadOpciones = async (preguntaId: number) => {
    try {
      const res = await api.get(`/admin/preguntas/${preguntaId}/opciones`);
      setOpciones(res.data);
    } catch (e) {
      console.error(e);
    }
  };

  const handleToggleCorrecta = async (opcion: Opcion) => {
    try {
      await api.put(`/admin/opciones/${opcion.id}`, { es_correcta: true });
      if (selectedPregunta) {
        loadOpciones(selectedPregunta.id);
      }
    } catch (e) {
      alert('Error al actualizar');
    }
  };

  const handleToggleCorrectaAll = async (opcion: Opcion) => {
    if (opcion.es_correcta) {
      try {
        await api.put(`/admin/opciones/${opcion.id}`, { es_correcta: false });
        if (selectedPregunta) {
          loadOpciones(selectedPregunta.id);
        }
      } catch (e) {
        alert('Error al actualizar');
      }
    } else {
      try {
        const otrasOpciones = opciones.filter(o => o.id !== opcion.id && o.es_correcta);
        const updates = otrasOpciones.map(o => 
          api.put(`/admin/opciones/${o.id}`, { es_correcta: false })
        );
        updates.push(api.put(`/admin/opciones/${opcion.id}`, { es_correcta: true }));
        await Promise.all(updates);
        if (selectedPregunta) {
          loadOpciones(selectedPregunta.id);
        }
      } catch (e) {
        alert('Error al actualizar');
      }
    }
  };

  const handleDeleteOpcion = async (opcionId: number, texto: string) => {
    if (!confirm(`¿Eliminar la opción "${texto}"?`)) return;
    try {
      await api.delete(`/admin/opciones/${opcionId}`);
      if (selectedPregunta) {
        loadOpciones(selectedPregunta.id);
      }
    } catch (e) {
      alert('Error al eliminar');
    }
  };

  const handleAddOpcion = async (preguntaId: number, texto: string, esCorrecta: boolean) => {
    try {
      await api.post(`/admin/preguntas/${preguntaId}/opciones`, { texto, es_correcta: esCorrecta });
      loadOpciones(preguntaId);
      return true;
    } catch (e) {
      alert('Error al agregar opción');
      return false;
    }
  };

  const openCreateModal = () => {
    setModalMode('create');
    setEditingItem(null);
    setShowModal(true);
  };

  const openEditModal = (item: any) => {
    setModalMode('edit');
    setEditingItem(item);
    setShowModal(true);
  };

  const handleDelete = async (endpoint: string, id: number, name: string) => {
    if (!confirm(`¿Eliminar ${name}?`)) return;
    try {
      await api.delete(`${endpoint}/${id}`);
      loadData();
    } catch (e) {
      alert('Error al eliminar');
    }
  };

  const handleAprobar = async (preguntaId: number) => {
    try {
      await api.post(`/admin/preguntas/${preguntaId}/aprobar`);
      loadData();
    } catch (e) {
      alert('Error al aprobar');
    }
  };

  const handleRechazar = async (preguntaId: number) => {
    const motivo = prompt('Motivo del rechazo:');
    if (!motivo) return;
    try {
      await api.post(`/admin/preguntas/${preguntaId}/rechazar`, motivo);
      loadData();
    } catch (e) {
      alert('Error al rechazar');
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const form = e.target as HTMLFormElement;
    const formData = new FormData(form);
    const data: any = {};
    formData.forEach((value, key) => {
      if (value !== '') data[key] = value;
    });

    if (data.activo === 'true') data.activo = true;
    if (data.activo === 'false') data.activo = false;
    if (data.es_correcta === 'true') data.es_correcta = true;

    try {
      if (modalMode === 'create') {
        const endpointMap: Record<string, string> = {
          'bloques': '/admin/bloques',
          'areas': '/admin/areas',
          'asignaturas': '/admin/asignaturas',
          'grupos-acad': '/admin/grupos-academicos',
          'especialidades': '/admin/especialidades',
          'config-puntaje': '/admin/config-puntaje',
          'cursos': '/admin/cursos',
          'temas': '/admin/temas',
          'preguntas': '/admin/preguntas',
        };
        await api.post(endpointMap[activeTab] || `/${activeTab}`, data);
      } else {
        const endpointMap: Record<string, string> = {
          'bloques': '/admin/bloques',
          'areas': '/admin/areas',
          'asignaturas': '/admin/asignaturas',
          'grupos-acad': '/admin/grupos-academicos',
          'especialidades': '/admin/especialidades',
          'config-puntaje': '/admin/config-puntaje',
          'cursos': '/admin/cursos',
          'temas': '/admin/temas',
          'preguntas': '/admin/preguntas',
        };
        await api.put(`${endpointMap[activeTab] || `/${activeTab}`}/${editingItem.id}`, data);
      }
      setShowModal(false);
      loadData();
    } catch (e: any) {
      alert(e.response?.data?.detail || 'Error al guardar');
    }
  };

  const renderForm = () => {
    switch (activeTab) {
      case 'bloques':
        return (
          <>
            <div className="mb-4">
              <label className="block text-sm font-medium mb-1">Código</label>
              <input name="codigo" defaultValue={editingItem?.codigo} className="w-full p-2 border rounded" required />
            </div>
            <div className="mb-4">
              <label className="block text-sm font-medium mb-1">Nombre</label>
              <input name="nombre" defaultValue={editingItem?.nombre} className="w-full p-2 border rounded" required />
            </div>
            <div className="mb-4">
              <label className="block text-sm font-medium mb-1">Descripción</label>
              <textarea name="descripcion" defaultValue={editingItem?.descripcion} className="w-full p-2 border rounded" />
            </div>
            <div className="mb-4">
              <label className="block text-sm font-medium mb-1">Orden</label>
              <input name="orden" type="number" defaultValue={editingItem?.orden || 0} className="w-full p-2 border rounded" />
            </div>
          </>
        );
      case 'areas':
        return (
          <>
            <div className="mb-4">
              <label className="block text-sm font-medium mb-1">Bloque</label>
              <select name="bloque_id" defaultValue={editingItem?.bloque_id} className="w-full p-2 border rounded" required>
                <option value="">Seleccionar...</option>
                {bloques.map(b => (
                  <option key={b.id} value={b.id}>{b.nombre}</option>
                ))}
              </select>
            </div>
            <div className="mb-4">
              <label className="block text-sm font-medium mb-1">Código</label>
              <input name="codigo" defaultValue={editingItem?.codigo} className="w-full p-2 border rounded" />
            </div>
            <div className="mb-4">
              <label className="block text-sm font-medium mb-1">Nombre</label>
              <input name="nombre" defaultValue={editingItem?.nombre} className="w-full p-2 border rounded" required />
            </div>
            <div className="mb-4">
              <label className="block text-sm font-medium mb-1">Descripción</label>
              <textarea name="descripcion" defaultValue={editingItem?.descripcion} className="w-full p-2 border rounded" />
            </div>
            <div className="mb-4">
              <label className="block text-sm font-medium mb-1">Orden</label>
              <input name="orden" type="number" defaultValue={editingItem?.orden || 0} className="w-full p-2 border rounded" />
            </div>
          </>
        );
      case 'asignaturas':
        return (
          <>
            <div className="mb-4">
              <label className="block text-sm font-medium mb-1">Área</label>
              <select name="area_id" defaultValue={editingItem?.area_id} className="w-full p-2 border rounded" required>
                <option value="">Seleccionar...</option>
                {areas.map(a => (
                  <option key={a.id} value={a.id}>{a.nombre}</option>
                ))}
              </select>
            </div>
            <div className="mb-4">
              <label className="block text-sm font-medium mb-1">Nombre</label>
              <input name="nombre" defaultValue={editingItem?.nombre} className="w-full p-2 border rounded" required />
            </div>
            <div className="mb-4">
              <label className="block text-sm font-medium mb-1">Descripción</label>
              <textarea name="descripcion" defaultValue={editingItem?.descripcion} className="w-full p-2 border rounded" />
            </div>
            <div className="mb-4">
              <label className="block text-sm font-medium mb-1">Orden</label>
              <input name="orden" type="number" defaultValue={editingItem?.orden || 0} className="w-full p-2 border rounded" />
            </div>
          </>
        );
      case 'grupos-acad':
        return (
          <>
            <div className="mb-4">
              <label className="block text-sm font-medium mb-1">Código</label>
              <input name="codigo" defaultValue={editingItem?.codigo} className="w-full p-2 border rounded" required />
            </div>
            <div className="mb-4">
              <label className="block text-sm font-medium mb-1">Nombre</label>
              <input name="nombre" defaultValue={editingItem?.nombre} className="w-full p-2 border rounded" required />
            </div>
            <div className="mb-4">
              <label className="block text-sm font-medium mb-1">Descripción</label>
              <textarea name="descripcion" defaultValue={editingItem?.descripcion} className="w-full p-2 border rounded" />
            </div>
            <div className="mb-4">
              <label className="block text-sm font-medium mb-1">Orden</label>
              <input name="orden" type="number" defaultValue={editingItem?.orden || 0} className="w-full p-2 border rounded" />
            </div>
          </>
        );
      case 'especialidades':
        return (
          <>
            <div className="mb-4">
              <label className="block text-sm font-medium mb-1">Código</label>
              <input name="codigo" defaultValue={editingItem?.codigo} className="w-full p-2 border rounded" required />
            </div>
            <div className="mb-4">
              <label className="block text-sm font-medium mb-1">Nombre</label>
              <input name="nombre" defaultValue={editingItem?.nombre} className="w-full p-2 border rounded" required />
            </div>
            <div className="mb-4">
              <label className="block text-sm font-medium mb-1">Grupo Académico</label>
              <select name="grupo_academico_id" defaultValue={editingItem?.grupo_academico_id} className="w-full p-2 border rounded" required>
                <option value="">Seleccionar...</option>
                {gruposAcad.map(g => (
                  <option key={g.id} value={g.id}>{g.nombre}</option>
                ))}
              </select>
            </div>
            <div className="mb-4">
              <label className="block text-sm font-medium mb-1">Puntaje Mínimo</label>
              <input name="puntaje_minimo" type="number" defaultValue={editingItem?.puntaje_minimo || 0} className="w-full p-2 border rounded" />
            </div>
            <div className="mb-4">
              <label className="block text-sm font-medium mb-1">Orden</label>
              <input name="orden" type="number" defaultValue={editingItem?.orden || 0} className="w-full p-2 border rounded" />
            </div>
          </>
        );
      case 'config-puntaje':
        return (
          <>
            <div className="mb-4">
              <label className="block text-sm font-medium mb-1">Grupo Académico</label>
              <select name="grupo_academico_id" defaultValue={editingItem?.grupo_academico_id} className="w-full p-2 border rounded" required>
                <option value="">Seleccionar...</option>
                {gruposAcad.map(g => (
                  <option key={g.id} value={g.id}>{g.nombre}</option>
                ))}
              </select>
            </div>
            <div className="mb-4">
              <label className="block text-sm font-medium mb-1">Asignatura</label>
              <select name="asignatura_id" defaultValue={editingItem?.asignatura_id} className="w-full p-2 border rounded" required>
                <option value="">Seleccionar...</option>
                {asignaturas.map(a => (
                  <option key={a.id} value={a.id}>{a.nombre}</option>
                ))}
              </select>
            </div>
            <div className="mb-4">
              <label className="block text-sm font-medium mb-1">Número de Preguntas</label>
              <input name="numero_preguntas" type="number" defaultValue={editingItem?.numero_preguntas || 0} className="w-full p-2 border rounded" required />
            </div>
            <div className="mb-4">
              <label className="block text-sm font-medium mb-1">Puntaje por Pregunta</label>
              <input name="puntaje_pregunta" type="number" step="any" defaultValue={editingItem?.puntaje_pregunta || 0} className="w-full p-2 border rounded" required />
            </div>
          </>
        );
      case 'preguntas':
        return (
          <>
            <div className="mb-4">
              <label className="block text-sm font-medium mb-1">Asignatura</label>
              <select name="asignatura_id" defaultValue={editingItem?.asignatura_id} className="w-full p-2 border rounded" required>
                <option value="">Seleccionar...</option>
                {asignaturas.map(a => (
                  <option key={a.id} value={a.id}>{a.nombre}</option>
                ))}
              </select>
            </div>
            <div className="mb-4">
              <label className="block text-sm font-medium mb-1">Enunciado</label>
              <textarea name="enunciado" defaultValue={editingItem?.enunciado} className="w-full p-2 border rounded" rows={3} required />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="mb-4">
                <label className="block text-sm font-medium mb-1">Universidad</label>
                <input name="universidad" defaultValue={editingItem?.universidad || 'UNPRG'} className="w-full p-2 border rounded" placeholder="UNPRG" />
              </div>
              <div className="mb-4">
                <label className="block text-sm font-medium mb-1">Año y Tipo</label>
                <input name="an_exam" defaultValue={editingItem?.an_exam} className="w-full p-2 border rounded" placeholder="2024-I Simulacro" />
              </div>
            </div>
            <div className="mb-4">
              <label className="block text-sm font-medium mb-1">URL Imagen (opcional)</label>
              <input name="imagen_url" defaultValue={editingItem?.imagen_url} className="w-full p-2 border rounded" placeholder="https://..." />
            </div>
            <div className="mb-4">
              <label className="block text-sm font-medium mb-1">Explicación</label>
              <textarea name="explicacion" defaultValue={editingItem?.explicacion} className="w-full p-2 border rounded" rows={2} placeholder="Por que es correcta..." />
            </div>
            <div className="mb-4">
              <label className="block text-sm font-medium mb-1">Dificultad</label>
              <select name="dificultad" defaultValue={editingItem?.dificultad || 2} className="w-full p-2 border rounded">
                <option value={1}>Fácil</option>
                <option value={2}>Medio</option>
                <option value={3}>Difícil</option>
              </select>
            </div>
            <div className="mb-4">
              <label className="flex items-center gap-2">
                <input type="checkbox" name="activa" defaultChecked={editingItem?.activa !== false} value="true" />
                <span>Activa</span>
              </label>
            </div>
          </>
        );
      case 'publicidad': {
        return (
          <div className="space-y-6">
            <p className="text-slate-600">Gestiona las imágenes publicitarias que aparecen en el dashboard de los usuarios.</p>

            {/* Formulario agregar */}
            <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl space-y-3">
              <h3 className="font-semibold text-slate-800">Agregar imagen</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-slate-600 mb-1">URL de la imagen *</label>
                  <input
                    type="url"
                    placeholder="https://..."
                    value={newPubUrl}
                    onChange={e => setNewPubUrl(e.target.value)}
                    className="w-full p-2 border rounded-lg text-sm"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-600 mb-1">Enlace al hacer clic (opcional)</label>
                  <input
                    type="url"
                    placeholder="https://..."
                    value={newPubLink}
                    onChange={e => setNewPubLink(e.target.value)}
                    className="w-full p-2 border rounded-lg text-sm"
                  />
                </div>
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-600 mb-1">Descripción (opcional)</label>
                <input
                  type="text"
                  placeholder="Descripción del anuncio..."
                  value={newPubDesc}
                  onChange={e => setNewPubDesc(e.target.value)}
                  className="w-full p-2 border rounded-lg text-sm"
                />
              </div>
              {newPubUrl && (
                <div className="rounded-lg overflow-hidden border border-slate-200" style={{height: '100px'}}>
                  <img src={newPubUrl} alt="Preview" className="w-full h-full object-cover"
                    onError={e => { (e.target as HTMLImageElement).style.display = 'none'; }} />
                </div>
              )}
              <button
                onClick={async () => {
                  if (!newPubUrl.trim()) return alert('La URL de imagen es requerida');
                  try {
                    await api.post('/admin/publicidad', { imagen_url: newPubUrl, enlace_url: newPubLink || null, descripcion: newPubDesc || null });
                    setNewPubUrl(''); setNewPubLink(''); setNewPubDesc('');
                    loadData();
                  } catch { alert('Error al agregar'); }
                }}
                className="px-4 py-2 bg-primary-600 text-white rounded-lg text-sm hover:bg-primary-700 transition-colors"
              >
                + Agregar imagen
              </button>
            </div>

            {/* Lista */}
            {publicidad.length === 0 ? (
              <div className="text-center py-8 text-slate-400">No hay imágenes de publicidad.</div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {publicidad.map(p => (
                  <div key={p.id} className={`border rounded-xl overflow-hidden ${p.activa ? 'border-slate-200' : 'border-slate-100 opacity-60'}`}>
                    <div className="relative" style={{height: '100px'}}>
                      <img src={p.imagen_url} alt={p.descripcion || ''} className="w-full h-full object-cover" />
                      <span className={`absolute top-2 right-2 px-2 py-0.5 rounded-full text-xs font-medium ${p.activa ? 'bg-green-500 text-white' : 'bg-slate-400 text-white'}`}>
                        {p.activa ? 'Activa' : 'Inactiva'}
                      </span>
                    </div>
                    <div className="p-3 space-y-2">
                      {p.descripcion && <p className="text-sm text-slate-600 truncate">{p.descripcion}</p>}
                      {p.enlace_url && <p className="text-xs text-blue-500 truncate">{p.enlace_url}</p>}
                      <div className="flex gap-2">
                        <button
                          onClick={async () => {
                            await api.put(\`/admin/publicidad/\${p.id}\`, { activa: !p.activa });
                            loadData();
                          }}
                          className={`flex-1 py-1.5 rounded-lg text-xs font-medium transition-colors ${p.activa ? 'bg-amber-100 text-amber-700 hover:bg-amber-200' : 'bg-green-100 text-green-700 hover:bg-green-200'}`}
                        >
                          {p.activa ? 'Desactivar' : 'Activar'}
                        </button>
                        <button
                          onClick={async () => {
                            if (!confirm('¿Eliminar esta imagen?')) return;
                            await api.delete(\`/admin/publicidad/\${p.id}\`);
                            loadData();
                          }}
                          className="px-3 py-1.5 bg-red-100 text-red-700 hover:bg-red-200 rounded-lg text-xs font-medium transition-colors"
                        >
                          Eliminar
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        );
      }
      default:
        return null;
    }
  };

  const renderTable = () => {
    switch (activeTab) {
      case 'usuarios':
        return (
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-200">
                <th className="text-left py-2">ID</th>
                <th className="text-left py-2">Email</th>
                <th className="text-left py-2">Rol</th>
                <th className="text-left py-2">Activo</th>
                <th className="text-left py-2">Fecha Registro</th>
              </tr>
            </thead>
            <tbody>
              {usuarios.map(u => (
                <tr key={u.id} className="border-b border-slate-100">
                  <td className="py-2">{u.id}</td>
                  <td className="py-2">{u.email}</td>
                  <td className="py-2">{u.rol_id === 2 ? 'Admin' : 'Usuario'}</td>
                  <td className="py-2">{u.activo ? 'Sí' : 'No'}</td>
                  <td className="py-2">{u.fecha_registro}</td>
                </tr>
              ))}
            </tbody>
          </table>
        );
      case 'bloques':
        return (
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-200">
                <th className="text-left py-2">Código</th>
                <th className="text-left py-2">Nombre</th>
                <th className="text-left py-2">Descripción</th>
                <th className="text-left py-2">Orden</th>
                <th className="text-left py-2">Acciones</th>
              </tr>
            </thead>
            <tbody>
              {bloques.map(b => (
                <tr key={b.id} className="border-b border-slate-100">
                  <td className="py-2">{b.codigo}</td>
                  <td className="py-2 font-medium">{b.nombre}</td>
                  <td className="py-2 text-slate-500">{b.descripcion}</td>
                  <td className="py-2">{b.orden}</td>
                  <td className="py-2">
                    <button onClick={() => openEditModal(b)} className="p-2 hover:bg-slate-200 rounded-lg">
                      <Edit className="w-4 h-4" />
                    </button>
                    <button onClick={() => handleDelete('/admin/bloques', b.id, b.nombre)} className="p-2 hover:bg-red-100 rounded-lg text-red-600">
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        );
      case 'areas':
        return (
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-200">
                <th className="text-left py-2">Código</th>
                <th className="text-left py-2">Nombre</th>
                <th className="text-left py-2">Bloque</th>
                <th className="text-left py-2">Orden</th>
                <th className="text-left py-2">Acciones</th>
              </tr>
            </thead>
            <tbody>
              {areas.map(a => (
                <tr key={a.id} className="border-b border-slate-100">
                  <td className="py-2">{a.codigo}</td>
                  <td className="py-2 font-medium">{a.nombre}</td>
                  <td className="py-2 text-slate-500">{a.bloque_nombre}</td>
                  <td className="py-2">{a.orden}</td>
                  <td className="py-2">
                    <button onClick={() => openEditModal(a)} className="p-2 hover:bg-slate-200 rounded-lg">
                      <Edit className="w-4 h-4" />
                    </button>
                    <button onClick={() => handleDelete('/admin/areas', a.id, a.nombre)} className="p-2 hover:bg-red-100 rounded-lg text-red-600">
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        );
      case 'asignaturas':
        return (
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-200">
                <th className="text-left py-2">Nombre</th>
                <th className="text-left py-2">Área</th>
                <th className="text-left py-2">Orden</th>
                <th className="text-left py-2">Acciones</th>
              </tr>
            </thead>
            <tbody>
              {asignaturas.map(a => (
                <tr key={a.id} className="border-b border-slate-100">
                  <td className="py-2 font-medium">{a.nombre}</td>
                  <td className="py-2 text-slate-500">{a.area_nombre}</td>
                  <td className="py-2">{a.orden}</td>
                  <td className="py-2">
                    <button onClick={() => openEditModal(a)} className="p-2 hover:bg-slate-200 rounded-lg">
                      <Edit className="w-4 h-4" />
                    </button>
                    <button onClick={() => handleDelete('/admin/asignaturas', a.id, a.nombre)} className="p-2 hover:bg-red-100 rounded-lg text-red-600">
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        );
      case 'grupos-acad':
        return (
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-200">
                <th className="text-left py-2">Código</th>
                <th className="text-left py-2">Nombre</th>
                <th className="text-left py-2">Descripción</th>
                <th className="text-left py-2">Orden</th>
                <th className="text-left py-2">Acciones</th>
              </tr>
            </thead>
            <tbody>
              {gruposAcad.map(g => (
                <tr key={g.id} className="border-b border-slate-100">
                  <td className="py-2">{g.codigo}</td>
                  <td className="py-2 font-medium">{g.nombre}</td>
                  <td className="py-2 text-slate-500">{g.descripcion}</td>
                  <td className="py-2">{g.orden}</td>
                  <td className="py-2">
                    <button onClick={() => openEditModal(g)} className="p-2 hover:bg-slate-200 rounded-lg">
                      <Edit className="w-4 h-4" />
                    </button>
                    <button onClick={() => handleDelete('/admin/grupos-academicos', g.id, g.nombre)} className="p-2 hover:bg-red-100 rounded-lg text-red-600">
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        );
      case 'especialidades':
        return (
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-200">
                <th className="text-left py-2">Código</th>
                <th className="text-left py-2">Nombre</th>
                <th className="text-left py-2">Grupo Académico</th>
                <th className="text-left py-2">Puntaje Min</th>
                <th className="text-left py-2">Acciones</th>
              </tr>
            </thead>
            <tbody>
              {especialidades.map(e => (
                <tr key={e.id} className="border-b border-slate-100">
                  <td className="py-2">{e.codigo}</td>
                  <td className="py-2 font-medium">{e.nombre}</td>
                  <td className="py-2 text-slate-500">{e.grupo_nombre}</td>
                  <td className="py-2">{e.puntaje_minimo}</td>
                  <td className="py-2">
                    <button onClick={() => openEditModal(e)} className="p-2 hover:bg-slate-200 rounded-lg">
                      <Edit className="w-4 h-4" />
                    </button>
                    <button onClick={() => handleDelete('/admin/especialidades', e.id, e.nombre)} className="p-2 hover:bg-red-100 rounded-lg text-red-600">
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        );
      case 'config-puntaje':
        const configsFiltradas = configPuntaje.filter(c => 
          !filtroGrupo || filtroGrupo === 'todos' || c.grupo_nombre === filtroGrupo
        );
        const configsAgrupadas = configsFiltradas.reduce((acc, c) => {
          const key = c.grupo_nombre;
          if (!acc[key]) acc[key] = [];
          acc[key].push(c);
          return acc;
        }, {} as Record<string, ConfigPuntaje[]>);
        const gruposUnicos = [...new Set(configPuntaje.map(c => c.grupo_nombre).filter(Boolean))];
        return (
          <div className="space-y-4">
            <div className="flex gap-4 flex-wrap items-center">
              <select
                value={filtroGrupo}
                onChange={(e) => setFiltroGrupo(e.target.value)}
                className="px-4 py-2 border rounded-lg"
              >
                <option value="todos">Todos los grupos ({gruposUnicos.length})</option>
                {gruposUnicos.map(g => (
                  <option key={g} value={g}>{g}</option>
                ))}
              </select>
              <span className="px-3 py-2 bg-slate-100 rounded-lg text-sm">
                {configsFiltradas.length} configs
              </span>
            </div>
            {Object.entries(configsAgrupadas).map(([grupo, configs]) => {
              const puntajeTotal = configs.reduce((sum, c) => sum + (c.numero_preguntas * c.puntaje_pregunta), 0);
              const totalPreguntas = configs.reduce((sum, c) => sum + c.numero_preguntas, 0);
              return (
                <details key={grupo} className="border rounded-lg overflow-hidden">
                  <summary className="px-4 py-3 bg-slate-50 cursor-pointer font-medium flex justify-between items-center">
                    <span>{grupo}</span>
                    <div className="flex gap-4 text-sm text-slate-500">
                      <span>{totalPreguntas} preg.</span>
                      <span className="font-semibold text-primary-600">{puntajeTotal} pts total</span>
                    </div>
                  </summary>
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-slate-200 bg-slate-50">
                        <th className="text-left py-2 px-4">Asignatura</th>
                        <th className="text-left py-2 w-24"># Preg.</th>
                        <th className="text-left py-2 w-24">Puntaje</th>
                        <th className="text-left py-2 w-24">Total</th>
                        <th className="text-left py-2 w-20">Act.</th>
                        <th className="text-left py-2 w-24">Acciones</th>
                      </tr>
                    </thead>
                    <tbody>
                      {configs.map(c => (
                        <tr key={c.id} className="border-b border-slate-100">
                          <td className="py-2 px-4 font-medium">{c.asignatura_nombre}</td>
                          <td className="py-2">{c.numero_preguntas}</td>
                          <td className="py-2">{c.puntaje_pregunta}</td>
                          <td className="py-2 font-semibold text-primary-600">
                            {c.numero_preguntas * c.puntaje_pregunta}
                          </td>
                          <td className="py-2">
                            <span className={`px-2 py-1 rounded text-xs ${c.activo ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'}`}>
                              {c.activo ? 'Sí' : 'No'}
                            </span>
                          </td>
                          <td className="py-2 flex gap-1">
                            <button onClick={() => openEditModal(c)} className="p-2 hover:bg-slate-200 rounded-lg">
                              <Edit className="w-4 h-4" />
                            </button>
                            <button onClick={() => handleDelete('/admin/config-puntaje', c.id, c.asignatura_nombre)} className="p-2 hover:bg-red-100 rounded-lg text-red-600">
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </details>
              );
            })}
            {configsFiltradas.length === 0 && (
              <div className="text-center py-8 text-slate-500">
                No hay configuraciones de puntaje.
              </div>
            )}
          </div>
        );
      case 'cursos':
        return (
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-200">
                <th className="text-left py-2">Nombre</th>
                <th className="text-left py-2">Descripción</th>
                <th className="text-left py-2">Orden</th>
                <th className="text-left py-2">Activo</th>
                <th className="text-left py-2">Acciones</th>
              </tr>
            </thead>
            <tbody>
              {cursos.map(c => (
                <tr key={c.id} className="border-b border-slate-100">
                  <td className="py-2 font-medium">{c.nombre}</td>
                  <td className="py-2 text-slate-500">{c.descripcion}</td>
                  <td className="py-2">{c.orden}</td>
                  <td className="py-2">{c.activo ? 'Sí' : 'No'}</td>
                  <td className="py-2">
                    <button onClick={() => openEditModal(c)} className="p-2 hover:bg-slate-200 rounded-lg">
                      <Edit className="w-4 h-4" />
                    </button>
                    <button onClick={() => handleDelete('/admin/cursos', c.id, c.nombre)} className="p-2 hover:bg-red-100 rounded-lg text-red-600">
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        );
      case 'temas':
        return (
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-200">
                <th className="text-left py-2">Nombre</th>
                <th className="text-left py-2">Curso</th>
                <th className="text-left py-2">Dificultad</th>
                <th className="text-left py-2">Activo</th>
                <th className="text-left py-2">Acciones</th>
              </tr>
            </thead>
            <tbody>
              {temas.map(t => (
                <tr key={t.id} className="border-b border-slate-100">
                  <td className="py-2 font-medium">{t.nombre}</td>
                  <td className="py-2 text-slate-500">{t.curso_nombre}</td>
                  <td className="py-2">{t.dificultad_base}</td>
                  <td className="py-2">{t.activo ? 'Sí' : 'No'}</td>
                  <td className="py-2">
                    <button onClick={() => openEditModal(t)} className="p-2 hover:bg-slate-200 rounded-lg">
                      <Edit className="w-4 h-4" />
                    </button>
                    <button onClick={() => handleDelete('/admin/temas', t.id, t.nombre)} className="p-2 hover:bg-red-100 rounded-lg text-red-600">
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        );
      case 'preguntas': {
        const preguntasFiltradas = preguntas.filter(p => {
          const matchAsig = filtroAsignatura === 'todas' || p.asignatura_nombre?.includes(filtroAsignatura);
          const matchBusq = busqueda === '' || p.enunciado.toLowerCase().includes(busqueda.toLowerCase());
          return matchAsig && matchBusq;
        });
        const preguntasAgrupadas = preguntasFiltradas.reduce((acc, p) => {
          const key = p.asignatura_nombre || 'Sin asignar';
          if (!acc[key]) acc[key] = [];
          acc[key].push(p);
          return acc;
        }, {} as Record<string, Pregunta[]>);
        const duplicates = Object.values(preguntasAgrupadas).flat().filter((p, i, arr) => 
          arr.some((o, j) => j < i && o.enunciado.trim() === p.enunciado.trim())
        ).map(p => p.id);
        const filterAsignaturas = [...new Set(preguntas.map(p => p.asignatura_nombre).filter(Boolean))];
        return (
          <div className="space-y-4">
            <div className="flex gap-4 flex-wrap items-center">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                <input
                  type="text"
                  placeholder="Buscar en enunciado..."
                  value={busqueda}
                  onChange={(e) => setBusqueda(e.target.value)}
                  className="pl-10 pr-4 py-2 border rounded-lg w-64"
                />
              </div>
              <select
                value={filtroAsignatura}
                onChange={(e) => setFiltroAsignatura(e.target.value)}
                className="px-4 py-2 border rounded-lg"
              >
                <option value="todas">Todas ({preguntas.length})</option>
                {filterAsignaturas.map(a => (
                  <option key={a} value={a}>{a}</option>
                ))}
              </select>
              <span className="px-3 py-2 bg-slate-100 rounded-lg text-sm">
                {preguntasFiltradas.length} preguntas
                {duplicates.length > 0 && (
                  <span className="ml-2 text-amber-600 font-medium">({duplicates.length} duplicadas)</span>
                )}
              </span>
            </div>
            {Object.entries(preguntasAgrupadas).map(([asignatura, preguntasAsig]) => {
              if (asignatura.includes('Sin asignar')) return null;
              return (
                <details key={asignatura} className="border rounded-lg overflow-hidden">
                  <summary className="px-4 py-3 bg-slate-50 cursor-pointer font-medium flex justify-between items-center">
                    <span>{asignatura}</span>
                    <span className="text-sm text-slate-500">{preguntasAsig.length} preguntas</span>
                  </summary>
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-slate-200 bg-slate-50">
                        <th className="text-left py-2 w-12">#</th>
                        <th className="text-left py-2">Enunciado</th>
                        <th className="text-left py-2 w-24">Universidad</th>
                        <th className="text-left py-2 w-32">Año/Tipo</th>
                        <th className="text-left py-2 w-20">Dif.</th>
                        <th className="text-left py-2 w-16">Act.</th>
                        <th className="text-left py-2 w-24">Acciones</th>
                      </tr>
                    </thead>
                    <tbody>
                      {preguntasAsig.map((p, idx) => (
                        <tr key={p.id} className={`border-b border-slate-100 ${duplicates.includes(p.id) ? 'bg-amber-50' : ''}`}>
                          <td className="py-2">{idx + 1}</td>
                          <td className="py-2 max-w-md">
                            <div className="truncate" title={p.enunciado}>{p.enunciado}</div>
                            {p.imagen_url && <span className="text-xs text-blue-500">📷 Imagen</span>}
                            {duplicates.includes(p.id) && <span className="text-xs text-amber-600 ml-2">⚠️ Duplicada</span>}
                          </td>
                          <td className="py-2 text-sm">{p.universidad || '-'}</td>
                          <td className="py-2 text-sm">{p.an_exam || '-'}</td>
                          <td className="py-2">
                            <span className={`px-2 py-1 rounded text-xs ${
                              p.dificultad === 1 ? 'bg-green-100 text-green-700' :
                              p.dificultad === 2 ? 'bg-yellow-100 text-yellow-700' :
                              'bg-red-100 text-red-700'
                            }`}>
                              {p.dificultad === 1 ? 'Fác' : p.dificultad === 2 ? 'Med' : 'Dif'}
                            </span>
                          </td>
                          <td className="py-2">
                            <span className={`px-2 py-1 rounded text-xs ${p.activa ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'}`}>
                              {p.activa ? 'Sí' : 'No'}
                            </span>
                          </td>
                          <td className="py-2 flex gap-1">
                            {p.estado !== 'aprobado' && (
                              <button onClick={() => handleAprobar(p.id)} className="p-2 hover:bg-green-100 rounded-lg text-green-600" title="Validar">
                                <CheckCircle className="w-4 h-4" />
                              </button>
                            )}
                            <button onClick={() => openEditModal(p)} className="p-2 hover:bg-slate-200 rounded-lg" title="Editar">
                              <Edit className="w-4 h-4" />
                            </button>
                            <button onClick={() => handleDelete('/admin/preguntas', p.id, p.enunciado.slice(0, 20))} className="p-2 hover:bg-red-100 rounded-lg text-red-600" title="Eliminar">
                              <Trash2 className="w-4 h-4" />
                            </button>
                            <button onClick={() => { setSelectedPregunta(p); loadOpciones(p.id); setShowOpcionesModal(true); }} className="p-2 hover:bg-blue-100 rounded-lg text-blue-600" title="Gestionar Respuestas">
                              <ListChecks className="w-4 h-4" />
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </details>
              );
            })}
            {preguntasFiltradas.length === 0 && (
              <div className="text-center py-8 text-slate-500">
                No hay preguntas que coincidan con los filtros.
              </div>
            )}
          </div>
        );
      }
      case 'novedades': {
        const preguntasPendientes = preguntas.filter(p => p.estado === 'pendiente');
        const preguntasAprobadas = preguntas.filter(p => p.estado === 'aprobado');
        const preguntasRechazadas = preguntas.filter(p => p.estado === 'rechazado');
        return (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 cursor-pointer" onClick={() => setFiltroEstado('pendiente')}>
                <div className="text-2xl font-bold text-amber-600">{preguntasPendientes.length}</div>
                <div className="text-sm text-amber-600">Pendientes</div>
              </div>
              <div className="bg-green-50 border border-green-200 rounded-lg p-4 cursor-pointer" onClick={() => setFiltroEstado('aprobado')}>
                <div className="text-2xl font-bold text-green-600">{preguntasAprobadas.length}</div>
                <div className="text-sm text-green-600">Aprobadas</div>
              </div>
              <div className="bg-red-50 border border-red-200 rounded-lg p-4 cursor-pointer" onClick={() => setFiltroEstado('rechazado')}>
                <div className="text-2xl font-bold text-red-600">{preguntasRechazadas.length}</div>
                <div className="text-sm text-red-600">Rechazadas</div>
              </div>
              <div className="bg-slate-50 border border-slate-200 rounded-lg p-4 cursor-pointer" onClick={() => setFiltroEstado('')}>
                <div className="text-2xl font-bold text-slate-600">{preguntas.length}</div>
                <div className="text-sm text-slate-600">Total</div>
              </div>
            </div>
            {(filtroEstado ? preguntas.filter(p => p.estado === filtroEstado) : preguntas).slice(0, 20).map(p => (
              <div key={p.id} className={`border rounded-lg p-4 ${p.estado === 'pendiente' ? 'border-amber-300 bg-amber-50' : ''}`}>
                <div className="flex justify-between items-start mb-2">
                  <div>
                    <span className="text-xs text-slate-500">{p.asignatura_nombre}</span>
                    {p.usuario_email && <span className="text-xs text-slate-400 ml-2">por {p.usuario_email}</span>}
                  </div>
                  <span className={`px-2 py-1 rounded text-xs ${
                    p.estado === 'aprobado' ? 'bg-green-100 text-green-700' :
                    p.estado === 'rechazado' ? 'bg-red-100 text-red-700' :
                    'bg-amber-100 text-amber-700'
                  }`}>
                    {p.estado === 'aprobado' ? 'Validado' : p.estado || 'pendiente'}
                  </span>
                </div>
                <div className="font-medium mb-2">{p.enunciado}</div>
                {p.explicacion && <div className="text-sm text-slate-500 mb-2">Explicación: {p.explicacion}</div>}
                {p.motivo_rechazo && <div className="text-sm text-red-500 mb-2">Motivo rechazo: {p.motivo_rechazo}</div>}
                <div className="flex gap-2">
                  {p.estado !== 'aprobado' && (
                    <button onClick={() => handleAprobar(p.id)} className="px-3 py-1 bg-green-500 text-white rounded hover:bg-green-600 flex items-center gap-1">
                      <CheckCircle className="w-4 h-4" /> Validar
                    </button>
                  )}
                  {p.estado !== 'rechazado' && p.estado !== 'aprobado' && (
                    <button onClick={() => handleRechazar(p.id)} className="px-3 py-1 bg-red-500 text-white rounded hover:bg-red-600 flex items-center gap-1">
                      <XCircle className="w-4 h-4" /> Rechazar
                    </button>
                  )}
                  <button onClick={() => { setSelectedPregunta(p); loadOpciones(p.id); setShowOpcionesModal(true); }} className="px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-600 flex items-center gap-1">
                    <ListChecks className="w-4 h-4" /> Ver respuestas
                  </button>
                </div>
              </div>
            ))}
            {preguntas.length === 0 && (
              <div className="text-center py-8 text-slate-500">
                No hay preguntas.
              </div>
            )}
          </div>
        );
      }
      case 'permisos': {
        const getPermisoEditando = (usuarioId: string, seccion: string, valorOriginal: boolean) => {
          if (permisosEditando[usuarioId]?.[seccion] !== undefined) {
            return permisosEditando[usuarioId][seccion];
          }
          return valorOriginal;
        };
        
        const togglePermisoEditando = (usuarioId: string, seccion: string, valorOriginal: boolean) => {
          setPermisosEditando(prev => ({
            ...prev,
            [usuarioId]: {
              ...(prev[usuarioId] || {}),
              [seccion]: !getPermisoEditando(usuarioId, seccion, valorOriginal)
            }
          }));
        };
        
        const guardarPermisos = async (usuarioId: string) => {
          const cambios = permisosEditando[usuarioId];
          if (!cambios) return;
          
          for (const [seccion, tieneAcceso] of Object.entries(cambios)) {
            await adminAPI.updatePermiso({
              usuario_id: usuarioId,
              seccion: seccion,
              tiene_acceso: tieneAcceso
            });
          }
          
          setPermisosEditando(prev => {
            const newState = { ...prev };
            delete newState[usuarioId];
            return newState;
          });
          
          loadData();
        };
        
        return (
          <div className="space-y-4">
            <p className="text-slate-600">Administra los permisos de acceso de cada usuario.</p>
            {usuarios.map(u => {
              const tieneCambios = permisosEditando[u.id] && Object.keys(permisosEditando[u.id]).length > 0;
              return (
                <Card key={u.id} className="p-4">
                  <div className="flex items-center justify-between mb-3">
                    <div>
                      <p className="font-semibold">{u.nombre}</p>
                      <p className="text-sm text-slate-500">{u.email}</p>
                    </div>
                    <button
                      onClick={() => guardarPermisos(u.id)}
                      disabled={!tieneCambios}
                      className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                        tieneCambios 
                          ? 'bg-primary-600 text-white hover:bg-primary-700' 
                          : 'bg-slate-200 text-slate-400 cursor-not-allowed'
                      }`}
                    >
                      Actualizar
                    </button>
                  </div>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                    {['dashboard', 'simulacros', 'temas_debiles', 'flashcards', 'comunidad'].map(seccion => {
                      const perm = (u.permisos || []).find((p: any) => p.seccion === seccion);
                      const valorOriginal = perm?.tiene_acceso !== false;
                      const valorEditado = getPermisoEditando(u.id, seccion, valorOriginal);
                      return (
                        <label key={seccion} className="flex items-center gap-2 cursor-pointer">
                          <input
                            type="checkbox"
                            checked={valorEditado}
                            onChange={() => togglePermisoEditando(u.id, seccion, valorOriginal)}
                            className="w-4 h-4 rounded text-primary-600"
                          />
                          <span className="text-sm capitalize">{seccion.replace('_', ' ')}</span>
                        </label>
                      );
                    })}
                  </div>
                </Card>
              );
            })}
          </div>
        );
      }
      case 'publicidad': {
        return (
          <div className="space-y-6">
            <p className="text-slate-600">Gestiona las imágenes publicitarias que aparecen en el dashboard de los usuarios.</p>

            {/* Formulario agregar */}
            <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl space-y-3">
              <h3 className="font-semibold text-slate-800">Agregar imagen</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-slate-600 mb-1">URL de la imagen *</label>
                  <input
                    type="url"
                    placeholder="https://..."
                    value={newPubUrl}
                    onChange={e => setNewPubUrl(e.target.value)}
                    className="w-full p-2 border rounded-lg text-sm"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-600 mb-1">Enlace al hacer clic (opcional)</label>
                  <input
                    type="url"
                    placeholder="https://..."
                    value={newPubLink}
                    onChange={e => setNewPubLink(e.target.value)}
                    className="w-full p-2 border rounded-lg text-sm"
                  />
                </div>
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-600 mb-1">Descripción (opcional)</label>
                <input
                  type="text"
                  placeholder="Descripción del anuncio..."
                  value={newPubDesc}
                  onChange={e => setNewPubDesc(e.target.value)}
                  className="w-full p-2 border rounded-lg text-sm"
                />
              </div>
              {newPubUrl && (
                <div className="rounded-lg overflow-hidden border border-slate-200" style={{height: '100px'}}>
                  <img src={newPubUrl} alt="Preview" className="w-full h-full object-cover"
                    onError={e => { (e.target as HTMLImageElement).style.display = 'none'; }} />
                </div>
              )}
              <button
                onClick={async () => {
                  if (!newPubUrl.trim()) return alert('La URL de imagen es requerida');
                  try {
                    await api.post('/admin/publicidad', { imagen_url: newPubUrl, enlace_url: newPubLink || null, descripcion: newPubDesc || null });
                    setNewPubUrl(''); setNewPubLink(''); setNewPubDesc('');
                    loadData();
                  } catch { alert('Error al agregar'); }
                }}
                className="px-4 py-2 bg-primary-600 text-white rounded-lg text-sm hover:bg-primary-700 transition-colors"
              >
                + Agregar imagen
              </button>
            </div>

            {/* Lista */}
            {publicidad.length === 0 ? (
              <div className="text-center py-8 text-slate-400">No hay imágenes de publicidad.</div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {publicidad.map(p => (
                  <div key={p.id} className={`border rounded-xl overflow-hidden ${p.activa ? 'border-slate-200' : 'border-slate-100 opacity-60'}`}>
                    <div className="relative" style={{height: '100px'}}>
                      <img src={p.imagen_url} alt={p.descripcion || ''} className="w-full h-full object-cover" />
                      <span className={`absolute top-2 right-2 px-2 py-0.5 rounded-full text-xs font-medium ${p.activa ? 'bg-green-500 text-white' : 'bg-slate-400 text-white'}`}>
                        {p.activa ? 'Activa' : 'Inactiva'}
                      </span>
                    </div>
                    <div className="p-3 space-y-2">
                      {p.descripcion && <p className="text-sm text-slate-600 truncate">{p.descripcion}</p>}
                      {p.enlace_url && <p className="text-xs text-blue-500 truncate">{p.enlace_url}</p>}
                      <div className="flex gap-2">
                        <button
                          onClick={async () => {
                            await api.put(\`/admin/publicidad/\${p.id}\`, { activa: !p.activa });
                            loadData();
                          }}
                          className={`flex-1 py-1.5 rounded-lg text-xs font-medium transition-colors ${p.activa ? 'bg-amber-100 text-amber-700 hover:bg-amber-200' : 'bg-green-100 text-green-700 hover:bg-green-200'}`}
                        >
                          {p.activa ? 'Desactivar' : 'Activar'}
                        </button>
                        <button
                          onClick={async () => {
                            if (!confirm('¿Eliminar esta imagen?')) return;
                            await api.delete(\`/admin/publicidad/\${p.id}\`);
                            loadData();
                          }}
                          className="px-3 py-1.5 bg-red-100 text-red-700 hover:bg-red-200 rounded-lg text-xs font-medium transition-colors"
                        >
                          Eliminar
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        );
      }
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 p-6">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-2xl font-bold mb-6">Panel de Administración</h1>
        
        <div className="flex gap-2 mb-6 flex-wrap">
          {tabs.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
                activeTab === tab.id
                  ? 'bg-primary-600 text-white'
                  : 'bg-white text-slate-700 hover:bg-slate-100'
              }`}
            >
              <tab.icon className="w-4 h-4" />
              {tab.label}
            </button>
          ))}
        </div>

        {loading ? (
          <div className="flex justify-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
          </div>
        ) : (
          <>
            {activeTab === 'dashboard' && stats && (
              <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-4">
                <Card className="p-4">
                  <div className="text-3xl font-bold text-primary-600">{stats.usuarios}</div>
                  <div className="text-slate-500">Usuarios</div>
                </Card>
                <Card className="p-4">
                  <div className="text-3xl font-bold text-primary-600">{stats.cursos}</div>
                  <div className="text-slate-500">Cursos</div>
                </Card>
                <Card className="p-4">
                  <div className="text-3xl font-bold text-primary-600">{stats.temas}</div>
                  <div className="text-slate-500">Temas</div>
                </Card>
                <Card className="p-4">
                  <div className="text-3xl font-bold text-primary-600">{stats.preguntas}</div>
                  <div className="text-slate-500">Preguntas</div>
                </Card>
                <Card className="p-4">
                  <div className="text-3xl font-bold text-primary-600">{stats.simulacros}</div>
                  <div className="text-slate-500">Simulacros</div>
                </Card>
                <Card className="p-4">
                  <div className="text-3xl font-bold text-primary-600">{stats.promedio}</div>
                  <div className="text-slate-500">Promedio</div>
                </Card>
                <Card className="p-4">
                  <div className="text-3xl font-bold text-primary-600">{stats.sesiones}</div>
                  <div className="text-slate-500">Sesiones</div>
                </Card>
              </div>
            )}

            {activeTab !== 'dashboard' && (
              <Card>
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-lg font-semibold capitalize">{activeTab.replace('-', ' ')}</h2>
                  {renderForm() && (
                    <button onClick={openCreateModal} className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700">
                      <Plus className="w-4 h-4" />
                      Agregar
                    </button>
                  )}
                </div>
                {renderTable()}
              </Card>
            )}
          </>
        )}
      </div>

      {showOpcionesModal && selectedPregunta && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <Card className="w-full max-w-2xl p-6 max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-4">
              <div>
                <h3 className="text-lg font-semibold">Respuestas</h3>
                <p className="text-sm text-slate-500 mt-1">Pregunta: {selectedPregunta.enunciado}</p>
              </div>
              <button onClick={() => { setShowOpcionesModal(false); setSelectedPregunta(null); }} className="p-2 hover:bg-slate-100 rounded-lg">
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="mb-4">
              <h4 className="font-medium mb-2">Agregar nueva opción</h4>
              <div className="flex gap-2">
                <input
                  type="text"
                  id="newOpcionTexto"
                  placeholder="Texto de la opción..."
                  className="flex-1 p-2 border rounded"
                />
                <label className="flex items-center gap-2 p-2">
                  <input type="checkbox" id="newOpcionCorrecta" />
                  <span>Correcta</span>
                </label>
                <button
                  onClick={() => {
                    const texto = (document.getElementById('newOpcionTexto') as HTMLInputElement).value;
                    const esCorrecta = (document.getElementById('newOpcionCorrecta') as HTMLInputElement).checked;
                    if (texto.trim()) {
                      handleAddOpcion(selectedPregunta.id, texto.trim(), esCorrecta);
                      (document.getElementById('newOpcionTexto') as HTMLInputElement).value = '';
                      (document.getElementById('newOpcionCorrecta') as HTMLInputElement).checked = false;
                    }
                  }}
                  className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
                >
                  <Plus className="w-4 h-4" />
                </button>
              </div>
            </div>

            <div className="border-t pt-4">
              <h4 className="font-medium mb-3">Opciones actuales ({opciones.length})</h4>
              {opciones.length === 0 ? (
                <div className="text-center py-8 text-slate-500">
                  Esta pregunta aún no tiene opciones. Agrega al menos una.
                </div>
              ) : (
                <div className="space-y-2">
                  {opciones.map((opcion, idx) => (
                    <div
                      key={opcion.id}
                      className={`flex items-center gap-3 p-3 rounded-lg border ${
                        opcion.es_correcta
                          ? 'bg-green-50 border-green-300'
                          : 'bg-white border-slate-200'
                      }`}
                    >
                      <span className="w-8 h-8 flex items-center justify-center rounded-full bg-slate-100 text-sm font-medium">
                        {String.fromCharCode(65 + idx)}
                      </span>
                      <span className="flex-1">{opcion.texto}</span>
                      {opcion.es_correcta && (
                        <span className="px-2 py-1 bg-green-500 text-white text-xs rounded">
                          Correcta
                        </span>
                      )}
                      <div className="flex gap-1">
                        <button
                          onClick={() => handleToggleCorrectaAll(opcion)}
                          className={`p-2 rounded-lg ${
                            opcion.es_correcta
                              ? 'hover:bg-orange-100 text-orange-600'
                              : 'hover:bg-green-100 text-green-600'
                          }`}
                          title={opcion.es_correcta ? 'Desmarcar como correcta' : 'Marcar como correcta'}
                        >
                          {opcion.es_correcta ? <X className="w-4 h-4" /> : <ListChecks className="w-4 h-4" />}
                        </button>
                        <button
                          onClick={() => handleDeleteOpcion(opcion.id!, opcion.texto)}
                          className="p-2 hover:bg-red-100 rounded-lg text-red-600"
                          title="Eliminar"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="mt-6 pt-4 border-t flex justify-between">
              <div className="text-sm text-slate-500">
                {opciones.filter(o => o.es_correcta).length === 1 ? (
                  <span className="text-green-600">✓ Respuesta correcta definida</span>
                ) : opciones.length === 0 ? (
                  <span className="text-orange-500">⚠ Agrega al menos una opción</span>
                ) : (
                  <span className="text-orange-500">⚠ Marca una opción como correcta</span>
                )}
              </div>
              <button
                onClick={() => { setShowOpcionesModal(false); setSelectedPregunta(null); }}
                className="px-4 py-2 bg-slate-200 rounded-lg hover:bg-slate-300"
              >
                Cerrar
              </button>
            </div>
          </Card>
        </div>
      )}

      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <Card className="w-full max-w-md p-6">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold">
                {modalMode === 'create' ? 'Agregar' : 'Editar'} {activeTab.replace('-', ' ')}
              </h3>
              <button onClick={() => setShowModal(false)} className="p-2 hover:bg-slate-100 rounded-lg">
                <X className="w-5 h-5" />
              </button>
            </div>
            <form onSubmit={handleSubmit}>
              {renderForm()}
              <div className="flex gap-2 mt-6">
                <button type="button" onClick={() => setShowModal(false)} className="flex-1 px-4 py-2 bg-slate-200 rounded-lg hover:bg-slate-300">
                  Cancelar
                </button>
                <button type="submit" className="flex-1 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700">
                  Guardar
                </button>
              </div>
            </form>
          </Card>
        </div>
      )}
    </div>
  );
}
