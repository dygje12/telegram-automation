# Panduan Praktik Terbaik Docstring dan Komentar

Dokumentasi yang baik adalah kunci untuk pemeliharaan dan kolaborasi proyek yang efektif. Untuk memastikan konsistensi dan kualitas, ikuti panduan berikut saat menulis docstring untuk kode Python dan komentar untuk kode JavaScript Anda.

## Untuk Kode Python (menggunakan Sphinx-style Docstrings)

Kami merekomendasikan penggunaan format docstring bergaya Sphinx untuk kode Python Anda. Ini memungkinkan Sphinx untuk secara otomatis mengekstrak informasi dan membangun dokumentasi yang komprehensif.

### Contoh Docstring Fungsi:

```python
def my_function(param1, param2):
    """
    Deskripsi singkat tentang fungsi ini.

    Deskripsi yang lebih panjang jika diperlukan, menjelaskan detail implementasi atau tujuan yang lebih luas.

    :param param1: Deskripsi `param1` dan tipenya.
    :type param1: str
    :param param2: Deskripsi `param2` dan tipenya.
    :type param2: int
    :returns: Deskripsi nilai yang dikembalikan dan tipenya.
    :rtype: bool
    :raises ValueError: Jika `param1` tidak valid.
    """
    # Implementasi fungsi
    pass
```

### Contoh Docstring Kelas:

```python
class MyClass:
    """
    Deskripsi singkat tentang kelas ini.

    Deskripsi yang lebih panjang jika diperlukan.

    :ivar attribute1: Deskripsi `attribute1`.
    :vartype attribute1: str
    """
    def __init__(self, value):
        """
        Inisialisasi objek MyClass.

        :param value: Nilai awal.
        :type value: any
        """
        self.attribute1 = value

    def my_method(self):
        """
        Deskripsi singkat tentang metode ini.

        :returns: Hasil metode.
        :rtype: float
        """
        pass
```

### Poin Penting:
*   **Ringkas dan Jelas:** Baris pertama docstring harus berupa ringkasan singkat (satu baris) tentang fungsi atau kelas.
*   **Detail:** Berikan deskripsi yang lebih rinci setelah baris ringkasan, jika diperlukan.
*   **Parameter (`:param`):** Jelaskan setiap parameter, termasuk tujuannya dan tipe datanya.
*   **Tipe Parameter (`:type`):** Secara eksplisit nyatakan tipe data parameter.
*   **Nilai Kembali (`:returns` dan `:rtype`):** Jelaskan apa yang dikembalikan oleh fungsi atau metode dan tipe datanya.
*   **Pengecualian (`:raises`):** Sebutkan pengecualian yang mungkin dimunculkan oleh fungsi atau metode.
*   **Contoh:** Jika memungkinkan, sertakan contoh penggunaan dalam docstring.

## Untuk Kode JavaScript (menggunakan JSDoc)

Untuk kode JavaScript, gunakan sintaks JSDoc dalam komentar Anda. Ini memungkinkan JSDoc untuk menghasilkan dokumentasi API yang interaktif.

### Contoh Komentar Fungsi:

```javascript
/**
 * Deskripsi singkat tentang fungsi ini.
 *
 * Deskripsi yang lebih panjang jika diperlukan.
 * @param {string} param1 - Deskripsi `param1`.
 * @param {number} param2 - Deskripsi `param2`.
 * @returns {boolean} Deskripsi nilai yang dikembalikan.
 * @throws {Error} Jika `param1` tidak valid.
 */
function myFunction(param1, param2) {
  // Implementasi fungsi
}
```

### Contoh Komentar Kelas:

```javascript
/**
 * Deskripsi singkat tentang kelas ini.
 *
 * Deskripsi yang lebih panjang jika diperlukan.
 * @class
 */
class MyClass {
  /**
   * Inisialisasi objek MyClass.
   * @param {*} value - Nilai awal.
   */
  constructor(value) {
    /**
     * Deskripsi `attribute1`.
     * @type {string}
     */
    this.attribute1 = value;
  }

  /**
   * Deskripsi singkat tentang metode ini.
   * @returns {number} Hasil metode.
   */
  myMethod() {
    // Implementasi metode
  }
}
```

### Poin Penting:
*   **Ringkas dan Jelas:** Baris pertama komentar harus berupa ringkasan singkat.
*   **`@param`:** Jelaskan setiap parameter, termasuk tipe data dan tujuannya.
*   **`@returns`:** Jelaskan nilai yang dikembalikan dan tipe datanya.
*   **`@throws`:** Sebutkan pengecualian yang mungkin dimunculkan.
*   **`@typedef`:** Gunakan untuk mendokumentasikan tipe data kustom atau objek kompleks.
*   **`@memberof` / `@static` / `@instance`:** Gunakan tag ini untuk mengorganisir dokumentasi Anda dengan lebih baik.

Dengan mengikuti panduan ini, kita dapat memastikan bahwa dokumentasi yang dihasilkan secara otomatis akurat, komprehensif, dan mudah digunakan oleh semua pengembang yang berkontribusi pada proyek ini.

