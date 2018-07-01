import tsl2561
import veml6070
import bme280

if __name__ == '__main__':

    veml = veml6070.Veml6070()
    uv_raw = veml.get_uva_light_intensity_raw()
    uv = veml.get_uva_light_intensity()
    print "UVA Light value : %f W/(m*m) from raw value %d" % (uv, uv_raw)

    temperature,pressure,humidity = bme280.readBME280All()

    print "Temperature : ", temperature, "C"
    print "Pressure : ", pressure, "hPa"
    print "Humidity : ", humidity, "%"
    
    (ch0,ch1)= tsl2561.readValues()
    print "Full Spectrum(IR + Visible) :%d lux" %ch0
    print "Infrared Value :%d lux" %ch1
    print "Visible Value :%d lux" %(ch0 - ch1)
