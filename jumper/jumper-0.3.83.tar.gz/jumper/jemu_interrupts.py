"""
:copyright: (c) 2017 by Jumper Labs Ltd.
:license: Apache 2.0, see LICENSE.txt for more details.
"""


class Interrupts(object):
    RESET = 'Reset'
    NMI = "NMI"
    HARD_FAULT = "Hard Fault"
    MEMORY_MANAGE_FAULT = "Memory Management Fault"
    BUS_FAULT = "Bus Fault"
    USAGE_FAULT = "Usage Fault"
    SVCALL = "Svcall"
    DEBUG_NON = "Debug Non"
    PENDSV = "Pendsv"
    SYSTICK = "Systick"

    # nrf52
    SPIM0_SPIS0_TWIM0_TWIS0_SPI0_TWI0 = "SPIM0_SPIS0_TWIM0_TWIS0_SPI0_TWI0"
    NFCT = "NFCT"
    CCM_AAR = "CCM_AAR"
    QDEC = "QDEC"
    COMP_LPCOMP = "COMP_LPCOMP"
    SWI0_EGU0 = "SWI0_EGU0"
    I2S = "I2S"
    FPU = "FPU"
    GPIOTE = "GPIOTE"
    UARTE0_UART0 = "UARTE0_UART0"
    TIMER0 = "TIMER0"
    TIMER1 = "TIMER1"
    TIMER2 = "TIMER2"
    TIMER3 = "TIMER3"
    TIMER4 = "TIMER4"
    RADIO = "RADIO"
    POWER_CLOCK = "POWER_CLOCK"
    RNG = "RNG"
    SPIM1_SPIS1_TWIM1_TWIS1_SPI1_TWI1 = "SPIM1_SPIS1_TWIM1_TWIS1_SPI1_TWI1"
    SWI1_EGU1 = "SWI1_EGU1"
    SWI2_EGU2 = "SWI2_EGU2"
    SWI3_EGU3 = "SWI3_EGU3"
    SWI4_EGU4 = "SWI4_EGU4"
    SWI5_EGU5 = "SWI5_EGU5"
    SPIM2_SPIS2_SPI2 = "SPIM2_SPIS2_SPI2"
    TEMP = "TEMP"
    RTC0 = "RTC0"
    RTC1 = "RTC1"
    RTC2 = "RTC2"
    WDT = "WDT"
    MWU = "MWU"
    ECB = "ECB"
    SAADC = "SAADC"
    PWM0 = "PWM0"
    PWM1 = "PWM1"
    PWM2 = "PWM2"

    # Stm32f4
    TAMP_STAMP = "TAMP_STAMP"
    EXTI0 = "EXTI0"
    EXTI1 = "EXTI1"
    EXTI2 = "EXTI2"
    EXTI3 = "EXTI3"
    EXTI4 = "EXTI4"
    EXTI9_5 = "EXTI9_5"
    EXTI15_10 = "EXTI15_10"
    ADC = "ADC"
    I2C2_EV = "I2C2_EV"
    I2C2_ER = "I2C2_ER"
    SDIO = "SDIO"
    TIM2 = "TIM2"
    TIM1_TRG_COM_TIM11 = "TIM1_TRG_COM_TIM11"
    TIM1_UP_TIM10 = "TIM1_UP_TIM10"
    TIM1_BRK_TIM9 = "TIM1_BRK_TIM9"
    TIM1_CC = "TIM1_CC"
    OTG_FS_WKUP = "OTG_FS_WKUP"
    OTG_FS = "OTG_FS"
    TIM3 = "TIM3"
    I2C1_EV = "I2C1_EV"
    I2C1_ER = "I2C1_ER"
    FLASH = "FLASH"


class JemuInterrupts(object):
    _INT = "interrupt"
    _DESCRIPTION = "description"

    def __init__(self):
        self._interrupt_callbacks = []
        self._jemu_connection = None

    def set_jemu_connection(self, jemu_connection):
        self._jemu_connection = jemu_connection
        self._jemu_connection.register(self.receive_packet)

    def on_interrupt(self, callback):
        self._interrupt_callbacks += callback

    def receive_packet(self, jemu_packet):
        if jemu_packet[self._DESCRIPTION] == self._INT:
            for callback in self._interrupt_callbacks:
                callback(jemu_packet['interrupt_type'])

