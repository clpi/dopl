class Ado < Formula
  desc "Ado - A Minimal Programming Language"
  homepage ""
  url ""
  sha256 ""
  license "MIT"

  def install
    system "make"
    bin.install "doc" => "ado"
  end

  test do
    (testpath/"test.do").write("print(\"hello from ado\")\n")
    assert_match "hello from ado", shell_output("#{bin}/ado test.do")
  end
end
