class Ado < Formula
  desc "Ado - A Minimal Programming Language"
  homepage "https://github.com/OWNER/REPO"
  url "https://github.com/OWNER/REPO/archive/refs/tags/v0.1.0.tar.gz"
  sha256 "REPLACE_WITH_SHA256"
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
