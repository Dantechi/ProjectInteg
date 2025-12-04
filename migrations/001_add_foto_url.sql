-- Agrega columnas de foto a tablas existentes (nullable)
ALTER TABLE refugio ADD COLUMN IF NOT EXISTS foto_url TEXT;
ALTER TABLE mascota ADD COLUMN IF NOT EXISTS foto_url TEXT;
