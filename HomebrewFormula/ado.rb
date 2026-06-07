class Ado < Formula
  desc "Ado - A Minimal Programming Language"
  homepage ""
  url ""
  sha256 ""
  license "MIT"

  depends_on "curl"
  depends_on "python"

  def install
    system "make"
    system "make", "DESTDIR=#{prefix}", "PREFIX=", "install"
  end

  test do
    (testpath/"test.do").write("print(\"hello from ado\")\n")
    assert_match "hello from ado", shell_output("#{bin}/ado test.do")
  end
end
