"""
Sistema Integral de Gestión de Clientes, Servicios y Reservas
Empresa: Software FJ
Curso: Programación - Código: 213023
Universidad Nacional Abierta y a Distancia
"""

import datetime
import logging
import os
from abc import ABC, abstractmethod
from typing import List, Optional

# ========================= CONFIGURACIÓN DE LOGS =========================
# Configuración del archivo de logs para registrar eventos y errores
LOG_FILE = "sistema_logs.log"

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()  # Para ver también en consola
    ]
)

# ======================== EXCEPCIONES PERSONALIZADAS ========================

class SistemaError(Exception):
    """Excepción base del sistema."""
    pass

class ClienteInvalidoError(SistemaError):
    """Excepción para datos de cliente inválidos."""
    pass

class ServicioNoDisponibleError(SistemaError):
    """Excepción para servicios no disponibles."""
    pass

class ReservaInvalidaError(SistemaError):
    """Excepción para reservas inválidas."""
    pass

class ParametroFaltanteError(SistemaError):
    """Excepción para parámetros faltantes."""
    pass

# ========================= CLASE ABSTRACTA ENTIDAD =========================

class Entidad(ABC):
    """
    Clase abstracta que representa entidades generales del sistema.
    Demuestra abstracción y método abstracto.
    """
    
    def __init__(self, id_entidad: str, nombre: str):
        """
        Constructor de la entidad.
        
        Args:
            id_entidad: Identificador único de la entidad
            nombre: Nombre descriptivo de la entidad
        """
        self._id_entidad = id_entidad  # Encapsulado
        self._nombre = nombre
    
    @abstractmethod
    def obtener_descripcion(self) -> str:
        """
        Método abstracto que debe ser implementado por las clases hijas.
        Demuestra polimorfismo.
        """
        pass
    
    # Getters y Setters (encapsulación)
    def get_id(self) -> str:
        return self._id_entidad
    
    def get_nombre(self) -> str:
        return self._nombre
    
    def set_nombre(self, nombre: str) -> None:
        if not nombre or len(nombre.strip()) == 0:
            raise ClienteInvalidoError("El nombre no puede estar vacío")
        self._nombre = nombre

# ========================= CLASE CLIENTE =========================

class Cliente(Entidad):
    """
    Clase Cliente con validaciones robustas y encapsulación de datos personales.
    """
    
    def __init__(self, id_cliente: str, nombre: str, email: str, telefono: str):
        """
        Constructor de Cliente con validaciones.
        
        Args:
            id_cliente: Identificador único del cliente
            nombre: Nombre completo del cliente
            email: Correo electrónico válido
            telefono: Número de teléfono
        """
        super().__init__(id_cliente, nombre)
        self._email = None
        self._telefono = None
        # Usar setters para validaciones
        self.set_email(email)
        self.set_telefono(telefono)
        logging.info(f"Cliente creado exitosamente: {nombre} (ID: {id_cliente})")
    
    def set_email(self, email: str) -> None:
        """Validación de email."""
        if not email or "@" not in email or "." not in email:
            raise ClienteInvalidoError(f"Email inválido: {email}")
        self._email = email
    
    def set_telefono(self, telefono: str) -> None:
        """Validación de teléfono (mínimo 7 dígitos)."""
        if not telefono or len(telefono.strip()) < 7:
            raise ClienteInvalidoError(f"Teléfono inválido: {telefono}")
        self._telefono = telefono
    
    def get_email(self) -> str:
        return self._email
    
    def get_telefono(self) -> str:
        return self._telefono
    
    def obtener_descripcion(self) -> str:
        """Implementación del método abstracto."""
        return f"Cliente: {self._nombre}, Email: {self._email}, Teléfono: {self._telefono}"
    
    def __str__(self) -> str:
        return self.obtener_descripcion()

# ========================= CLASE ABSTRACTA SERVICIO =========================

class Servicio(Entidad, ABC):
    """
    Clase abstracta Servicio que define el contrato para todos los servicios.
    """
    
    def __init__(self, id_servicio: str, nombre: str, precio_base: float):
        super().__init__(id_servicio, nombre)
        if precio_base < 0:
            raise ServicioNoDisponibleError("El precio base no puede ser negativo")
        self._precio_base = precio_base
    
    @abstractmethod
    def calcular_costo(self, duracion_horas: float = 1, **kwargs) -> float:
        """
        Calcula el costo del servicio. Demuestra polimorfismo.
        
        Args:
            duracion_horas: Duración en horas
            **kwargs: Parámetros adicionales (descuentos, impuestos, etc.)
        """
        pass
    
    @abstractmethod
    def validar_parametros(self, **kwargs) -> bool:
        """Valida los parámetros específicos del servicio."""
        pass
    
    def get_precio_base(self) -> float:
        return self._precio_base

# ========================= SERVICIOS ESPECIALIZADOS =========================

class ReservaSalas(Servicio):
    """Servicio de reserva de salas."""
    
    def __init__(self, id_servicio: str, nombre: str, precio_base: float, capacidad_maxima: int):
        super().__init__(id_servicio, nombre, precio_base)
        self._capacidad_maxima = capacidad_maxima
    
    def calcular_costo(self, duracion_horas: float = 1, **kwargs) -> float:
        """
        Calcula costo para reserva de salas.
        Método sobrecargado mediante parámetros opcionales.
        """
        try:
            costo = self._precio_base * duracion_horas
            
            # Aplicar descuento si se proporciona
            descuento = kwargs.get('descuento', 0.0)
            if descuento < 0 or descuento > 100:
                raise ParametroFaltanteError(f"Descuento inválido: {descuento}")
            
            costo = costo * (1 - descuento / 100)
            
            # Aplicar impuesto si se solicita
            aplicar_impuesto = kwargs.get('aplicar_impuesto', False)
            if aplicar_impuesto:
                costo = costo * 1.19  # 19% IVA
            
            return round(costo, 2)
        except Exception as e:
            logging.error(f"Error en calcular_costo de ReservaSalas: {str(e)}")
            raise
    
    def validar_parametros(self, **kwargs) -> bool:
        """Valida los parámetros para reserva de salas."""
        duracion = kwargs.get('duracion_horas', 0)
        if duracion <= 0:
            raise ServicioNoDisponibleError("La duración debe ser mayor a 0 horas")
        if duracion > 24:
            raise ServicioNoDisponibleError("La duración no puede exceder 24 horas")
        return True
    
    def obtener_descripcion(self) -> str:
        return f"Reserva de Salas: {self._nombre} - Capacidad: {self._capacidad_maxima}"

class AlquilerEquipos(Servicio):
    """Servicio de alquiler de equipos."""
    
    def __init__(self, id_servicio: str, nombre: str, precio_base: float, tipo_equipo: str):
        super().__init__(id_servicio, nombre, precio_base)
        self._tipo_equipo = tipo_equipo
    
    def calcular_costo(self, duracion_horas: float = 1, **kwargs) -> float:
        """Calcula costo para alquiler de equipos."""
        try:
            cantidad = kwargs.get('cantidad', 1)
            if cantidad <= 0:
                raise ParametroFaltanteError("La cantidad debe ser mayor a 0")
            
            costo = self._precio_base * duracion_horas * cantidad
            
            # Descuento por cantidad
            if cantidad >= 5:
                costo = costo * 0.90  # 10% descuento
            
            return round(costo, 2)
        except Exception as e:
            logging.error(f"Error en calcular_costo de AlquilerEquipos: {str(e)}")
            raise
    
    def validar_parametros(self, **kwargs) -> bool:
        """Valida los parámetros para alquiler de equipos."""
        cantidad = kwargs.get('cantidad', 0)
        if cantidad <= 0:
            raise ServicioNoDisponibleError("La cantidad de equipos debe ser mayor a 0")
        if cantidad > 50:
            raise ServicioNoDisponibleError("No se pueden alquilar más de 50 equipos")
        return True
    
    def obtener_descripcion(self) -> str:
        return f"Alquiler de Equipos: {self._nombre} - Tipo: {self._tipo_equipo}"

class AsesoriasEspecializadas(Servicio):
    """Servicio de asesorías especializadas."""
    
    def __init__(self, id_servicio: str, nombre: str, precio_base: float, especialidad: str):
        super().__init__(id_servicio, nombre, precio_base)
        self._especialidad = especialidad
    
    def calcular_costo(self, duracion_horas: float = 1, **kwargs) -> float:
        """Calcula costo para asesorías especializadas."""
        try:
            costo = self._precio_base * duracion_horas
            
            # Descuento por cliente frecuente
            es_frecuente = kwargs.get('es_frecuente', False)
            if es_frecuente:
                costo = costo * 0.85  # 15% descuento
            
            return round(costo, 2)
        except Exception as e:
            logging.error(f"Error en calcular_costo de AsesoriasEspecializadas: {str(e)}")
            raise
    
    def validar_parametros(self, **kwargs) -> bool:
        """Valida los parámetros para asesorías."""
        duracion = kwargs.get('duracion_horas', 0)
        if duracion <= 0:
            raise ServicioNoDisponibleError("La duración debe ser mayor a 0 horas")
        if duracion > 8:
            raise ServicioNoDisponibleError("Una asesoría no puede durar más de 8 horas")
        return True
    
    def obtener_descripcion(self) -> str:
        return f"Asesorías Especializadas: {self._nombre} - Especialidad: {self._especialidad}"

# ========================= CLASE RESERVA =========================

class Reserva:
    """
    Clase Reserva que integra cliente, servicio, duración y estado.
    Implementa confirmación, cancelación y procesamiento con manejo de excepciones.
    """
    
    _contador_reservas = 0  # Atributo de clase para generar IDs únicos
    
    def __init__(self, cliente: Cliente, servicio: Servicio, duracion_horas: float, fecha: datetime.datetime = None):
        """
        Constructor de Reserva con validaciones.
        
        Args:
            cliente: Objeto Cliente
            servicio: Objeto Servicio
            duracion_horas: Duración en horas
            fecha: Fecha y hora de la reserva (por defecto ahora)
        """
        Reserva._contador_reservas += 1
        self._id_reserva = f"RES-{Reserva._contador_reservas:04d}"
        self._cliente = cliente
        self._servicio = servicio
        self._duracion_horas = duracion_horas
        self._fecha = fecha if fecha else datetime.datetime.now()
        self._estado = "PENDIENTE"  # PENDIENTE, CONFIRMADA, CANCELADA, COMPLETADA
        
        # Validar servicio antes de crear la reserva
        try:
            servicio.validar_parametros(duracion_horas=duracion_horas)
        except Exception as e:
            raise ReservaInvalidaError(f"No se puede crear la reserva: {str(e)}")
        
        logging.info(f"Reserva creada: {self._id_reserva} para {cliente.get_nombre()}")
    
    # Métodos sobrecargados para diferentes formas de calcular costos
    def calcular_costo_total(self) -> float:
        """Calcula costo base sin extras."""
        return self._servicio.calcular_costo(self._duracion_horas)
    
    def calcular_costo_total(self, descuento: float = 0.0) -> float:
        """Sobrecarga: calcula costo con descuento."""
        return self._servicio.calcular_costo(self._duracion_horas, descuento=descuento)
    
    def calcular_costo_total(self, descuento: float = 0.0, impuesto: bool = False) -> float:
        """Sobrecarga: calcula costo con descuento e impuesto."""
        return self._servicio.calcular_costo(self._duracion_horas, descuento=descuento, aplicar_impuesto=impuesto)
    
    def confirmar(self) -> bool:
        """Confirma la reserva."""
        if self._estado != "PENDIENTE":
            raise ReservaInvalidaError(f"No se puede confirmar una reserva en estado {self._estado}")
        self._estado = "CONFIRMADA"
        logging.info(f"Reserva {self._id_reserva} confirmada")
        return True
    
    def cancelar(self) -> bool:
        """Cancela la reserva."""
        if self._estado == "COMPLETADA":
            raise ReservaInvalidaError("No se puede cancelar una reserva completada")
        self._estado = "CANCELADA"
        logging.info(f"Reserva {self._id_reserva} cancelada")
        return True
    
    def completar(self) -> bool:
        """Completa la reserva."""
        if self._estado == "CONFIRMADA":
            self._estado = "COMPLETADA"
            logging.info(f"Reserva {self._id_reserva} completada")
            return True
        raise ReservaInvalidaError(f"No se puede completar reserva en estado {self._estado}")
    
    def obtener_info(self) -> str:
        """Obtiene información completa de la reserva."""
        return (f"Reserva: {self._id_reserva}\n"
                f"Cliente: {self._cliente.get_nombre()}\n"
                f"Servicio: {self._servicio.get_nombre()}\n"
                f"Duración: {self._duracion_horas} horas\n"
                f"Fecha: {self._fecha.strftime('%Y-%m-%d %H:%M')}\n"
                f"Estado: {self._estado}\n"
                f"Costo total: ${self.calcular_costo_total()}")
    
    def __str__(self) -> str:
        return self.obtener_info()

# ========================= SISTEMA PRINCIPAL =========================

class SistemaGestion:
    """
    Sistema principal que gestiona clientes, servicios y reservas.
    """
    
    def __init__(self):
        self._clientes: List[Cliente] = []
        self._servicios: List[Servicio] = []
        self._reservas: List[Reserva] = []
        logging.info("Sistema de Gestión inicializado")
    
    def registrar_cliente(self, id_cliente: str, nombre: str, email: str, telefono: str) -> Optional[Cliente]:
        """
        Registra un nuevo cliente con manejo de excepciones.
        """
        try:
            # Validar que el ID no exista
            for c in self._clientes:
                if c.get_id() == id_cliente:
                    raise ClienteInvalidoError(f"Ya existe un cliente con ID {id_cliente}")
            
            cliente = Cliente(id_cliente, nombre, email, telefono)
            self._clientes.append(cliente)
            logging.info(f"Cliente registrado: {cliente.get_nombre()}")
            return cliente
        except ClienteInvalidoError as e:
            logging.error(f"Error al registrar cliente: {str(e)}")
            return None
        except Exception as e:
            logging.error(f"Error inesperado al registrar cliente: {str(e)}")
            return None
    
    def agregar_servicio(self, servicio: Servicio) -> bool:
        """Agrega un servicio al sistema."""
        try:
            if not isinstance(servicio, Servicio):
                raise ServicioNoDisponibleError("El objeto no es un servicio válido")
            self._servicios.append(servicio)
            logging.info(f"Servicio agregado: {servicio.get_nombre()}")
            return True
        except Exception as e:
            logging.error(f"Error al agregar servicio: {str(e)}")
            return False
    
    def crear_reserva(self, id_cliente: str, id_servicio: str, duracion_horas: float, 
                      fecha: datetime.datetime = None) -> Optional[Reserva]:
        """
        Crea una reserva con manejo de excepciones.
        """
        try:
            # Buscar cliente
            cliente = None
            for c in self._clientes:
                if c.get_id() == id_cliente:
                    cliente = c
                    break
            
            if not cliente:
                raise ReservaInvalidaError(f"Cliente con ID {id_cliente} no encontrado")
            
            # Buscar servicio
            servicio = None
            for s in self._servicios:
                if s.get_id() == id_servicio:
                    servicio = s
                    break
            
            if not servicio:
                raise ReservaInvalidaError(f"Servicio con ID {id_servicio} no encontrado")
            
            # Crear reserva
            reserva = Reserva(cliente, servicio, duracion_horas, fecha)
            self._reservas.append(reserva)
            return reserva
            
        except ReservaInvalidaError as e:
            logging.error(f"Error al crear reserva: {str(e)}")
            return None
        except Exception as e:
            logging.error(f"Error inesperado al crear reserva: {str(e)}")
            return None
    
    def listar_clientes(self) -> List[Cliente]:
        return self._clientes.copy()
    
    def listar_servicios(self) -> List[Servicio]:
        return self._servicios.copy()
    
    def listar_reservas(self) -> List[Reserva]:
        return self._reservas.copy()
    
    def mostrar_estadisticas(self) -> None:
        """Muestra estadísticas del sistema."""
        print("\n" + "="*50)
        print("ESTADÍSTICAS DEL SISTEMA")
        print("="*50)
        print(f"Total clientes: {len(self._clientes)}")
        print(f"Total servicios: {len(self._servicios)}")
        print(f"Total reservas: {len(self._reservas)}")
        
        # Reservas por estado
        estados = {}
        for r in self._reservas:
            estado = r._estado
            estados[estado] = estados.get(estado, 0) + 1
        
        print("Reservas por estado:")
        for estado, cantidad in estados.items():
            print(f"  - {estado}: {cantidad}")

# ========================= FUNCIÓN PRINCIPAL Y DEMOSTRACIÓN =========================

def demostracion_sistema():
    """
    Función que demuestra al menos 10 operaciones completas,
    incluyendo registros válidos e inválidos, demostrando manejo de errores.
    """
    
    print("\n" + "="*60)
    print("SISTEMA INTEGRAL DE GESTIÓN - SOFTWARE FJ")
    print("Demostración con manejo de excepciones")
    print("="*60)
    
    sistema = SistemaGestion()
    
    # ==================== OPERACIÓN 1: Registrar cliente válido ====================
    print("\n[OPERACIÓN 1] Registrar cliente válido")
    cliente1 = sistema.registrar_cliente("C001", "Ana María Rodríguez", "ana@email.com", "3001234567")
    if cliente1:
        print(f"✓ Cliente registrado: {cliente1}")
    
    # ==================== OPERACIÓN 2: Registrar cliente inválido (email incorrecto) ====================
    print("\n[OPERACIÓN 2] Registrar cliente con email inválido")
    cliente_invalido = sistema.registrar_cliente("C002", "Juan Pérez", "email_invalido", "3109876543")
    if not cliente_invalido:
        print("✓ Error capturado correctamente: Cliente inválido no fue registrado")
    
    # ==================== OPERACIÓN 3: Registrar cliente con teléfono inválido ====================
    print("\n[OPERACIÓN 3] Registrar cliente con teléfono inválido")
    cliente_invalido2 = sistema.registrar_cliente("C003", "Pedro López", "pedro@email.com", "123")
    if not cliente_invalido2:
        print("✓ Error capturado correctamente: Teléfono inválido")
    
    # ==================== OPERACIÓN 4: Crear servicios válidos ====================
    print("\n[OPERACIÓN 4] Crear servicios disponibles")
    sala = ReservaSalas("S001", "Sala de Conferencias", 50000, 30)
    equipo = AlquilerEquipos("E001", "Laptop HP", 15000, "Computador")
    asesoria = AsesoriasEspecializadas("A001", "Asesoría en Python", 80000, "Programación")
    
    sistema.agregar_servicio(sala)
    sistema.agregar_servicio(equipo)
    sistema.agregar_servicio(asesoria)
    print("✓ Servicios creados y agregados al sistema")
    
    # ==================== OPERACIÓN 5: Registrar más clientes válidos ====================
    print("\n[OPERACIÓN 5] Registrar clientes adicionales")
    sistema.registrar_cliente("C004", "María Gómez", "maria@email.com", "3115556677")
    sistema.registrar_cliente("C005", "Carlos Ruiz", "carlos@email.com", "3228889900")
    print("✓ Clientes adicionales registrados")
    
    # ==================== OPERACIÓN 6: Crear reserva exitosa ====================
    print("\n[OPERACIÓN 6] Crear reserva exitosa (Sala de conferencias - 3 horas)")
    reserva1 = sistema.crear_reserva("C001", "S001", 3)
    if reserva1:
        reserva1.confirmar()
        print(f"✓ Reserva creada: Costo = ${reserva1.calcular_costo_total()}")
    
    # ==================== OPERACIÓN 7: Crear reserva con servicio inexistente ====================
    print("\n[OPERACIÓN 7] Intentar reserva con servicio inexistente")
    reserva_fallida = sistema.crear_reserva("C001", "S999", 2)
    if not reserva_fallida:
        print("✓ Error capturado correctamente: Servicio no existe")
    
    # ==================== OPERACIÓN 8: Crear reserva con cliente inexistente ====================
    print("\n[OPERACIÓN 8] Intentar reserva con cliente inexistente")
    reserva_fallida2 = sistema.crear_reserva("C999", "S001", 2)
    if not reserva_fallida2:
        print("✓ Error capturado correctamente: Cliente no existe")
    
    # ==================== OPERACIÓN 9: Reserva con duración inválida ====================
    print("\n[OPERACIÓN 9] Intentar reserva con duración inválida (25 horas)")
    reserva_invalida = sistema.crear_reserva("C001", "S001", 25)  # 25 > 24
    if not reserva_invalida:
        print("✓ Error capturado correctamente: Duración inválida")
    
    # ==================== OPERACIÓN 10: Cancelar reserva ====================
    print("\n[OPERACIÓN 10] Cancelar reserva existente")
    if reserva1:
        try:
            reserva1.cancelar()
            print("✓ Reserva cancelada exitosamente")
        except Exception as e:
            print(f"Error: {e}")
    
    # ==================== OPERACIONES ADICIONALES ====================
    # Operación 11: Usar sobrecarga de métodos para calcular costo con descuento
    print("\n[OPERACIÓN 11] Calcular costo con descuento (sobrecarga de métodos)")
    try:
        costo_base = sala.calcular_costo(2)
        costo_con_descuento = sala.calcular_costo(2, descuento=15)
        costo_con_impuesto = sala.calcular_costo(2, aplicar_impuesto=True)
        print(f"✓ Costo base (2h): ${costo_base}")
        print(f"✓ Costo con 15% descuento: ${costo_con_descuento}")
        print(f"✓ Costo con impuesto 19%: ${costo_con_impuesto}")
    except Exception as e:
        print(f"Error en cálculo: {e}")
    
    # Operación 12: Completar una reserva
    print("\n[OPERACIÓN 12] Crear y completar otra reserva")
    reserva2 = sistema.crear_reserva("C004", "A001", 2)
    if reserva2:
        reserva2.confirmar()
        reserva2.completar()
        print("✓ Reserva completada exitosamente")
    
    # Mostrar estadísticas finales
    sistema.mostrar_estadisticas()
    
    # Mostrar ubicación del archivo de logs
    print("\n" + "="*60)
    print(f"Archivo de logs generado: {os.path.abspath(LOG_FILE)}")
    print("Todos los errores y eventos han sido registrados.")
    print("="*60)


if __name__ == "__main__":
    demostracion_sistema()