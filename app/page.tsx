"use client";

import { useState } from "react";
import { Upload, FileText, CheckCircle, ArrowRight, Loader2 } from "lucide-react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";

export default function Home() {
  const router = useRouter();
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({
    name: "",
    name: "",
    cvText: ""
  });

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      setFile(selectedFile);
      setLoading(true);

      const data = new FormData();
      data.append("file", selectedFile);

      try {
        const res = await fetch("/api/parse-cv", {
          method: "POST",
          body: data,
        });
        const json = await res.json();

        if (json.text) {
          setFormData(prev => ({ ...prev, cvText: json.text }));
          // Simple heuristic to extract name (first line)
          const lines = json.text.split('\n').filter((l: string) => l.trim().length > 0);
          if (lines.length > 0) {
            setFormData(prev => ({ ...prev, name: lines[0].substring(0, 50) }));
          }
        }
      } catch (err) {
        console.error("Failed to parse", err);
        alert("Gagal membaca CV. Silakan coba lagi atau isi manual.");
      } finally {
        setLoading(false);
      }
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.cvText) {
      alert("Mohon isi atau upload CV terlebih dahulu.");
      return;
    }

    // Pass data via localStorage to Results page (simplest for this migration)
    localStorage.setItem("userProfile", JSON.stringify(formData));
    router.push("/results");
  };

  return (
    <main className="min-h-screen relative overflow-hidden">
      {/* Background Gradients */}
      <div className="absolute top-0 left-0 w-full h-[500px] bg-gradient-main opacity-20 blur-3xl -z-10" />

      <div className="max-w-6xl mx-auto px-6 py-20">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-16"
        >
          <h1 className="text-5xl md:text-7xl font-bold mb-6 bg-clip-text text-transparent bg-gradient-to-r from-orange-400 to-yellow-300">
            Digital Talent Platform
          </h1>
          <p className="text-xl text-gray-400 max-w-2xl mx-auto">
            Temukan potensi karir digital Anda melalui analisis AI berbasis SKKNI dan rekomendasi course yang terpersonalisasi.
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.2 }}
          className="bg-[#1c1f2b] border border-gray-800 rounded-3xl p-8 md:p-12 shadow-2xl max-w-4xl mx-auto"
        >
          <div className="grid md:grid-cols-2 gap-12">
            {/* Left: Upload */}
            <div className="space-y-6">
              <div className="flex items-center space-x-4 mb-4">
                <div className="w-10 h-10 rounded-full bg-orange-500/20 flex items-center justify-center text-orange-500 font-bold">1</div>
                <h3 className="text-xl font-semibold">Upload CV Anda</h3>
              </div>

              <div className="border-2 border-dashed border-gray-700 hover:border-orange-500 transition-colors rounded-2xl p-8 text-center cursor-pointer relative group">
                <input
                  type="file"
                  accept=".pdf,.docx,.txt"
                  onChange={handleFileUpload}
                  className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                />
                <div className="flex flex-col items-center space-y-4">
                  <div className="w-16 h-16 rounded-full bg-[#252a3d] flex items-center justify-center group-hover:scale-110 transition-transform">
                    {loading ? <Loader2 className="animate-spin text-orange-400" /> : <Upload className="text-gray-400 group-hover:text-orange-400" />}
                  </div>
                  <div>
                    <p className="font-medium text-white group-hover:text-orange-300">
                      {file ? file.name : "Klik atau drag CV ke sini"}
                    </p>
                    <p className="text-sm text-gray-500 mt-1">PDF, DOCX (Max 2MB)</p>
                  </div>
                </div>
              </div>

              {formData.cvText && (
                <div className="flex items-center text-green-400 text-sm bg-green-900/20 p-3 rounded-lg">
                  <CheckCircle className="w-4 h-4 mr-2" />
                  CV berhasil dianalisis!
                </div>
              )}
            </div>

            {/* Right: Form */}
            <div className="space-y-6">
              <div className="flex items-center space-x-4 mb-4">
                <div className="w-10 h-10 rounded-full bg-yellow-500/20 flex items-center justify-center text-yellow-500 font-bold">2</div>
                <h3 className="text-xl font-semibold">Lengkapi Profil</h3>
              </div>

              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="block text-sm text-gray-400 mb-1">Nama Lengkap</label>
                  <input
                    type="text"
                    required
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    className="w-full bg-[#0f1117] border border-gray-700 rounded-xl px-4 py-3 focus:border-orange-500 focus:outline-none transition-colors"
                    placeholder="John Doe"
                  />
                </div>

                <div>
                  <label className="block text-sm text-gray-400 mb-1">Ringkasan Profil / CV Text</label>
                  <textarea
                    required
                    value={formData.cvText}
                    onChange={(e) => setFormData({ ...formData, cvText: e.target.value })}
                    className="w-full bg-[#0f1117] border border-gray-700 rounded-xl px-4 py-3 focus:border-orange-500 focus:outline-none transition-colors h-32 text-sm"
                    placeholder="Paste CV Anda di sini jika tidak upload file..."
                  />
                </div>

                <button
                  type="submit"
                  className="w-full bg-gradient-to-r from-orange-600 to-yellow-500 hover:from-orange-500 hover:to-yellow-400 text-black font-bold py-4 rounded-xl shadow-lg hover:shadow-orange-500/20 transition-all flex items-center justify-center space-x-2"
                >
                  <span>Analisis Profil Saya</span>
                  <ArrowRight className="w-5 h-5" />
                </button>
              </form>
            </div>
          </div>
        </motion.div>
      </div>
    </main>
  );
}
