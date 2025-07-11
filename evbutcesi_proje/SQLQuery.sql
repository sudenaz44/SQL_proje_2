-- Kullanicilar tablosu
CREATE TABLE Kullanicilar (
    KullaniciID INT PRIMARY KEY IDENTITY(1,1),
    Ad NVARCHAR(50),
    Soyad NVARCHAR(50)
);

-- Kategoriler tablosu
CREATE TABLE Kategoriler (
    KategoriID INT PRIMARY KEY IDENTITY(1,1),
    KategoriAdi NVARCHAR(50)
);

-- Gelirler tablosu
CREATE TABLE Gelirler (
    GelirID INT PRIMARY KEY IDENTITY(1,1),
    KullaniciID INT,
    Tutar DECIMAL(10,2),
    Tarih DATE,
    Aciklama NVARCHAR(100),
    FOREIGN KEY (KullaniciID) REFERENCES Kullanicilar(KullaniciID)
);

-- Giderler tablosu
CREATE TABLE Giderler (
    GiderID INT PRIMARY KEY IDENTITY(1,1),
    KullaniciID INT,
    KategoriID INT,
    Tutar DECIMAL(10,2),
    Tarih DATE,
    Aciklama NVARCHAR(100),
    FOREIGN KEY (KullaniciID) REFERENCES Kullanicilar(KullaniciID),
    FOREIGN KEY (KategoriID) REFERENCES Kategoriler(KategoriID)
);


INSERT INTO Kullanicilar (Ad, Soyad) VALUES
('Sude', 'KILIÇ'),
('Yigit', 'KILIÇ'),
('Mert', 'KILIÇ');


INSERT INTO Kategoriler (KategoriAdi) VALUES
('Market'),
('Kira'),
('Fatura'),
('Eðlence');


INSERT INTO Gelirler (KullaniciID, Tutar, Tarih, Aciklama) VALUES
(1, 10000, '2025-07-01', 'Maaþ'),
(2, 8000, '2025-07-01', 'Maaþ'),
(3, 12000, '2025-07-01', 'Maaþ');

DELETE FROM Gelirler;


INSERT INTO Giderler (KullaniciID, KategoriID, Tutar, Tarih, Aciklama) VALUES
(1, 1, 500, '2025-07-02', 'Market alýþveriþi'),
(1, 2, 2000, '2025-07-03', 'Kira'),
(2, 1, 400, '2025-07-02', 'Market alýþveriþi'),
(2, 3, 300, '2025-07-04', 'Elektrik faturasý'),
(3, 4, 600, '2025-07-05', 'Yüzme giriþi');

Select * FROM Gelirler;


SELECT KullaniciID, SUM(Tutar) AS ToplamGelir
FROM Gelirler
GROUP BY KullaniciID;


SELECT KullaniciID, SUM(Tutar) AS ToplamGider
FROM Giderler
GROUP BY KullaniciID;

SELECT k.KategoriAdi, AVG(g.Tutar) AS OrtalamaHarcama
FROM Giderler g
INNER JOIN Kategoriler k ON g.KategoriID = k.KategoriID
GROUP BY k.KategoriAdi;


SELECT TOP 1 KullaniciID, MAX(Tutar) AS EnBuyukGider
FROM Giderler
GROUP BY KullaniciID
ORDER BY EnBuyukGider DESC;

--- sadeced id deðil ad soyad da geldi.

SELECT TOP 1 ku.Ad, ku.Soyad, MAX(g.Tutar) AS EnBuyukGider
FROM Giderler g
INNER JOIN Kullanicilar ku ON g.KullaniciID = ku.KullaniciID
GROUP BY ku.Ad, ku.Soyad
ORDER BY EnBuyukGider DESC;


SELECT g.GiderID, k.KategoriAdi, g.Tutar,
    CASE 
        WHEN g.Tutar >= 1000 THEN 'Lüks'
        ELSE 'Normal'
    END AS HarcamaDurumu
FROM Giderler g
INNER JOIN Kategoriler k ON g.KategoriID = k.KategoriID;

---toplam gelir gider farký

SELECT ku.Ad, ku.Soyad,
    ISNULL(gelirler.ToplamGelir, 0) - ISNULL(giderler.ToplamGider, 0) AS NetDurum
FROM Kullanicilar ku
LEFT JOIN (
    SELECT KullaniciID, SUM(Tutar) AS ToplamGelir
    FROM Gelirler
    GROUP BY KullaniciID
) AS gelirler ON ku.KullaniciID = gelirler.KullaniciID
LEFT JOIN (
    SELECT KullaniciID, SUM(Tutar) AS ToplamGider
    FROM Giderler
    GROUP BY KullaniciID
) AS giderler ON ku.KullaniciID = giderler.KullaniciID;



CREATE TABLE LogTablosu (
    LogID INT PRIMARY KEY IDENTITY(1,1),
    Mesaj NVARCHAR(255),
    Tarih DATETIME DEFAULT GETDATE()
);


CREATE TRIGGER trg_GelirEklendi
ON Gelirler
AFTER INSERT
AS
BEGIN
    INSERT INTO LogTablosu (Mesaj)
    SELECT 'Yeni gelir eklendi: ' + CAST(Tutar AS NVARCHAR(50)) + ' TL'
    FROM inserted;
END;


CREATE TRIGGER trg_GiderEklendi
ON Giderler
AFTER INSERT
AS
BEGIN
    INSERT INTO LogTablosu (Mesaj)
    SELECT 'Yeni gider eklendi: ' + CAST(Tutar AS NVARCHAR(50)) + ' TL'
    FROM inserted;
END;

INSERT INTO Gelirler (KullaniciID, Tutar, Tarih, Aciklama)
VALUES (1, 5000, '2025-07-15', 'Ek iþ-mesai');

SELECT * FROM LogTablosu;


